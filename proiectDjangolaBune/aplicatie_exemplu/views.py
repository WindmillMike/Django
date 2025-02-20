from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Product
from .forms import ProductFilterForm
from .forms import ContactForm
from .forms import ProductForm
from .forms import CustomUserRegistrationForm
from .models import Category
from .models import CustomUser
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.core.mail import send_mail
from django.conf import settings
import uuid
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from django.template.loader import render_to_string
from django.utils.timezone import now
from django.contrib import messages
from .models import Promotie, Vizualizare
from .forms import PromotieForm
from django.db import models
from django.core.mail import mail_admins
from .utils import trimite_mail_promotii
import logging
from django.db.models import F
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User, Group


def index(request):
	return HttpResponse("Primul raspuns")

def filter_products(request):
    form = ProductFilterForm(request.GET)
    products = Product.objects.all()
    categories = Category.objects.all()

    if form.is_valid():
        if form.cleaned_data.get('name'):
            name_filter = form.cleaned_data['name'].strip()
            products = products.filter(name__icontains=name_filter)

        if form.cleaned_data.get('category'):
            products = products.filter(category=form.cleaned_data['category'])

        if form.cleaned_data.get('min_price') is not None:
            products = products.filter(price__gte=form.cleaned_data['min_price'])

        if form.cleaned_data.get('max_price') is not None:
            products = products.filter(price__lte=form.cleaned_data['max_price'])

        if form.cleaned_data.get('min_stock') is not None:
            products = products.filter(stock_quantity__gte=form.cleaned_data['min_stock'])

        if form.cleaned_data.get('max_stock') is not None:
            products = products.filter(stock_quantity__lte=form.cleaned_data['max_stock'])

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  
        data = list(products.values('name', 'price', 'stock_quantity', 'category__name'))
        return JsonResponse({'products': data})

    return render(request, 'product_filter.html', {'form': form, 'products': products, 'categories': categories})

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()  # Salvăm datele într-un fișier JSON
            return render(request, 'contact_success.html')  # Pagina de succes
    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form})


@login_required
def add_product(request):
    # Verificăm dacă utilizatorul are permisiunea `add_product`
    if not request.user.has_perm('app.add_product'):
        return render(request, "403.html", {
            "titlu": "Eroare adaugare produse",
            "mesaj_personalizat": "Nu ai voie să adaugi produse."
        }, status=403)

    product = None  # Inițial nu avem produs

    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=True)  # Salvăm produsul cu prețul final calculat
            return redirect('add_product')  # Redirecționăm după salvare
    else:
        form = ProductForm()

    return render(request, 'add_product.html', {
        'form': form,
        'product': product
    })
    
##############lab6

logger = logging.getLogger('django')

def register(request):
    if request.method == 'POST':
        logger.debug("Cerere POST primită pentru înregistrare.")  # DEBUG 1
        form = CustomUserRegistrationForm(request.POST, request.FILES)

        if form.is_valid():
            username = form.cleaned_data.get("username")
            email = form.cleaned_data.get("email")

            if username.lower() == "admin":
                logger.warning(f"Încercare de înregistrare cu username interzis: {username}, email: {email}")  # WARNING 1
                mail_admins(
                    subject="Cineva încearcă să ne preia site-ul!",
                    message=f"O încercare de înregistrare cu username-ul 'admin' a fost făcută de pe email-ul {email}.",
                    html_message=f"<h1 style='color: red;'>Încercare suspectă!</h1><p>Email: <strong>{email}</strong></p>"
                )
                return JsonResponse({"success": False, "error": "Nu poți folosi acest username."})

            user = form.save(commit=False)
            user.cod = str(uuid.uuid4().hex)[:20] 
            user.email_confirmat = False  
            user.save()

            logger.info(f"Utilizator nou înregistrat: {username}, email: {email}")  # INFO 1

            confirmation_link = request.build_absolute_uri(reverse('confirm_email', args=[user.cod]))

            email_body = render_to_string('email_confirmation.html', {
                'user': user,
                'confirmation_link': confirmation_link
            })

            send_mail(
                subject="Confirmare cont - Magazin",
                message='',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=email_body
            )

            return JsonResponse({
                "success": True,
                "message": "Cont creat cu succes! Verifică e-mailul pentru confirmare.",
                "redirect_url": reverse('login')
            })

        logger.warning(f"Înregistrare eșuată: erori {form.errors}")  # WARNING 2
        return JsonResponse({"success": False, "errors": form.errors})

    else:
        logger.debug("Cerere GET pentru pagina de înregistrare.")  # DEBUG 2
        form = CustomUserRegistrationForm()

    return render(request, 'register.html', {'form': form})



#task 3 lab 6
logger = logging.getLogger(__name__)

def get_client_ip(request):
    """ Obține IP-ul utilizatorului. """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

import logging

logger = logging.getLogger('django')

def custom_login(request):
    if request.method == "POST":
        logger.debug("Cerere POST primită pentru login.")  # DEBUG 1
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            ip_address = get_client_ip(request)

            if 'failed_login_attempts' not in request.session:
                request.session['failed_login_attempts'] = 0
                request.session['last_failed_attempt'] = None

            if user is None:
                now = datetime.now()
                last_attempt = request.session.get('last_failed_attempt')

                if last_attempt and (now - datetime.fromisoformat(last_attempt)) < timedelta(minutes=2):
                    request.session['failed_login_attempts'] += 1
                else:
                    request.session['failed_login_attempts'] = 1

                request.session['last_failed_attempt'] = now.isoformat()

                logger.info(f"[SECURITY] Încercare eșuată {request.session['failed_login_attempts']} pentru {username} de la {ip_address}")  # INFO 1

                if request.session['failed_login_attempts'] >= 3:
                    logger.warning(f"[ALERT] Logări suspecte detectate pentru {username} de la {ip_address}!")  # WARNING 1

                    mail_admins(
                        subject="Logări suspecte detectate",
                        message=f"S-au detectat 3 încercări eșuate de logare pentru userul {username} de la IP-ul {ip_address} în mai puțin de 2 minute.",
                        html_message=f"<h1 style='color: red;'>Logări suspecte</h1><p><strong>User:</strong> {username}</p><p><strong>IP:</strong> {ip_address}</p>"
                    )

                return JsonResponse({'success': False, 'error': "Credentiale greșite"}, status=400)

            request.session['failed_login_attempts'] = 0
            request.session['last_failed_attempt'] = None
            
            if not user.email_confirmat:
                logger.error(f"Login eșuat: utilizatorul {username} nu și-a confirmat emailul.")  # ERROR 1
                return JsonResponse({'success': False, 'error': "Trebuie să-ți confirmi e-mailul înainte de a te autentifica."}, status=400)

            if username.lower() == "admin":
                logger.critical(f"[CRITICAL ALERT] Încercare de logare cu admin de la {ip_address}")  # CRITICAL 1

                mail_admins(
                    subject="Încercare de logare cu admin!",
                    message=f"Un utilizator a încercat să se logheze cu username-ul 'admin' de la IP-ul {ip_address}.",
                    html_message=f"<h1 style='color: red;'>Alertă: Încercare de logare cu admin</h1><p><strong>IP:</strong> {ip_address}</p>"
                )

            login(request, user)
            logger.info(f"Autentificare reușită pentru utilizatorul: {username}")  # INFO 2

            return JsonResponse({'success': True, 'redirect_url': '/aplicatie_exemplu/profile'})

    logger.debug("Cerere GET pentru pagina de login.")  # DEBUG 2
    form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})




@login_required
def profile(request):
    """ Pagina de profil care afișează datele utilizatorului din baza de date. """
    user = request.user  # Obține utilizatorul logat din baza de date

    user_data = {
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'is_staff': user.is_staff,  # Dacă utilizatorul este administrator
        'date_joined': user.date_joined.strftime('%d-%m-%Y %H:%M'),
        'last_login': user.last_login.strftime('%d-%m-%Y %H:%M') if user.last_login else "Niciodată",
    }

    return render(request, 'profile.html', {'user_data': user_data})

@login_required
def change_password(request):
    """ Permite utilizatorului să își schimbe parola. """
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Evită deconectarea utilizatorului
            return redirect('profile')  
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'change_password.html', {'form': form})

def custom_logout(request):
    logout(request)
    return redirect('login')  

##lab 7

def confirm_email(request, cod):
    logger.debug(f"Confirmare email primită pentru cod: {cod}")  # DEBUG 4
    user = get_object_or_404(CustomUser, cod=cod)  

    if not user.email_confirmat:
        user.email_confirmat = True 
        user.cod = None  
        user.save()
        logger.info(f"Email confirmat pentru utilizatorul: {user.username}")  # INFO 4
        messages.success(request, "E-mail confirmat cu succes! Acum te poți autentifica.")
    else:
        logger.warning(f"Emailul a fost deja confirmat pentru utilizatorul: {user.username}")  # WARNING 3

    return redirect('login')



##lab 7 task 2
MAX_VIZUALIZARI = 5  # N = 5

def inregistreaza_vizualizare(request, product_id):
    if request.user.is_authenticated:
        produs = get_object_or_404(Product, id=product_id)
        Vizualizare.objects.create(utilizator=request.user, produs=produs, data_vizualizare=now())

        # Ștergem cea mai veche vizualizare dacă sunt mai mult de MAX_VIZUALIZARI
        vizualizari = Vizualizare.objects.filter(utilizator=request.user).order_by('-data_vizualizare')
        if vizualizari.count() > MAX_VIZUALIZARI:
            vizualizari.last().delete()
            


def creare_promotie(request):
    K = 3  # Minim K vizualizări pentru a primi promoția

    if request.method == 'POST':
        form = PromotieForm(request.POST)
        if form.is_valid():
            promotie = form.save(commit=False)
            promotie.save()
            form.save_m2m()  # Salvăm categoriile promoției

            categorii_selectate = form.cleaned_data['categorii']

            # Selectăm utilizatorii care au vizualizat produse din categoriile promoției de minim K ori
            utilizatori_promo = {}
            for categorie in categorii_selectate:
                utilizatori = Vizualizare.objects.filter(
                    produs__category=categorie
                ).values('utilizator').annotate(numar_vizualizari=models.Count('id')).filter(numar_vizualizari__gte=K)

                utilizatori_promo[categorie.name] = [u['utilizator'] for u in utilizatori]

            # Trimitere e-mailuri cu `send_mass_mail()`
            trimite_mail_promotii(utilizatori_promo, promotie)
            messages.success(request, "Promoția a fost creată și e-mailurile au fost trimise!")
            return redirect('creare_promotie')  # Redirecționare la aceeași pagină pentru o nouă promoție

    else:
        form = PromotieForm()
    
    return render(request, 'promotii.html', {'form': form})

def lista_promotii(request):
    promotii = Promotie.objects.all()
    return render(request, 'lista_promotii.html', {'promotii': promotii})


def produs_detail(request, nume_produs):
    produs = get_object_or_404(Product, name=nume_produs)  # Găsim produsul după nume

    if request.user.is_authenticated:
        vizualizare = Vizualizare.objects.filter(utilizator=request.user, produs=produs)

        if vizualizare.exists():
            vizualizare.update(numar_vizualizari=F('numar_vizualizari') + 1, data_vizualizare=now())
        else:
            Vizualizare.objects.create(utilizator=request.user, produs=produs, numar_vizualizari=1)

    return render(request, 'produs_detail.html', {'produs': produs})


def lista_produse(request):
    """ Afișează lista produselor """
    produse = Product.objects.all()
    return render(request, 'product_list.html', {'produse': produse})


####lab 8 task 1
def custom_403_view(request, exception):
    mesaj = "Nu ai permisiunea de a accesa această resursă."
    
    # Verificăm motivul erorii și personalizăm mesajul
    if hasattr(exception, 'args') and exception.args:
        mesaj = exception.args[0]

    context = {
        "titlu": "Acces interzis!",
        "mesaj_personalizat": mesaj
    }
    return render(request, "403.html", context, status=403)

@login_required
def pagina_protejata(request):
    return HttpResponseForbidden("Aceasta este o pagină protejată.")

@permission_required('app.can_access_secret_page', raise_exception=True)
def pagina_restrictionata(request):
    return custom_403_view(request, Exception("Această pagină este disponibilă doar pentru administratori."))


###lab 8 task 2
def adauga_utilizator_la_grup():
    try:
        user = CustomUser.objects.get(username="nume_utilizator")  # Modifică cu un username real
        group = Group.objects.get(name="Administratori_produse")
        user.groups.add(group)
        user.save()
        print(f"Utilizatorul {user.username} a fost adăugat în grupul Administratori_produse.")
    except CustomUser.DoesNotExist:
        print("Utilizatorul nu există.")
    except Group.DoesNotExist:
        print("Grupul nu există.")