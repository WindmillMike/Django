# Django imports
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail, mail_admins
from django.db import models
from django.db.models import F
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.timezone import now
from django.utils.http import url_has_allowed_host_and_scheme

# Local imports
from .models import Product, Category, CustomUser, Promotie, Vizualizare
from .forms import ProductFilterForm, ContactForm, ProductForm, CustomUserRegistrationForm, PromotieForm
from .utils import trimite_mail_promotii

# Other imports
import uuid
import logging
from datetime import datetime, timedelta



def index(request):
    return render(request, "index.html")


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
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Mesajul tău a fost trimis cu succes! 📩")
            return redirect("home")
        else:
            messages.warning(request, "Verifică câmpurile completate. Există erori în formular. ⚠️")
    else:
        form = ContactForm()

    return render(request, "contact.html", {"form": form})


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
    
@login_required
def add_product_view(request):
    if not request.user.is_staff:
        messages.error(request, "Nu ai permisiunea de a adăuga produse. 🚫")
        return redirect("home")

    if request.method == "POST":
        messages.debug(request, "Se încearcă adăugarea unui produs... 🛍️")
        # Logica de adăugare a produsului
        messages.success(request, "Produs adăugat cu succes! 🎉")
        return redirect("products")

    return render(request, "add_product.html")
    
##############lab6

logger = logging.getLogger('django')

def register(request):
    if request.method == 'POST':
        logger.debug("Cerere POST primită pentru înregistrare.")  # DEBUG

        form = CustomUserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            email = form.cleaned_data.get("email")

            # Interzicere username "admin"
            if username.lower() == "admin":
                logger.warning(f"Încercare de înregistrare cu username interzis: {username}, email: {email}")  # WARNING
                mail_admins(
                    subject="Încercare de înregistrare suspectă",
                    message=f"O încercare de înregistrare cu username-ul 'admin' a fost făcută de pe email-ul {email}.",
                    html_message=f"<h1 style='color: red;'>Încercare suspectă!</h1><p>Email: <strong>{email}</strong></p>"
                )
                messages.error(request, "Nu poți folosi acest username.")
                return redirect('register')

            user = form.save(commit=False)
            user.cod = str(uuid.uuid4().hex)[:20] 
            user.email_confirmat = False  
            user.save()

            logger.info(f"Utilizator nou înregistrat: {username}, email: {email}")  # INFO

            # Creare link de confirmare email
            confirmation_link = request.build_absolute_uri(reverse('confirm_email', args=[user.cod]))

            email_body = render_to_string('email_confirmation.html', {
                'user': user,
                'confirmation_link': confirmation_link
            })

            # Trimitere email de confirmare
            send_mail(
                subject="Confirmare cont - Magazin",
                message='',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=email_body
            )

            messages.success(request, "Cont creat cu succes! Verifică e-mailul pentru confirmare.")
            return redirect('login')  

        logger.warning(f"Înregistrare eșuată: erori {form.errors}")  # WARNING
        messages.error(request, "Înregistrare eșuată. Verifică datele introduse.")
    
    else:
        logger.debug("Cerere GET pentru pagina de înregistrare.")  # DEBUG
        form = CustomUserRegistrationForm()

    return render(request, 'register.html', {'form': form})



def register_view(request):
    if request.method == "POST":
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Cont creat cu succes! Te poți autentifica acum. ✅")
            return redirect("login")
        else:
            messages.error(request, "Eroare la înregistrare. Verifică datele introduse. ❌")

    else:
        form = CustomUserRegistrationForm()

    return render(request, "register.html", {"form": form})



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

            # 🔹 Verificăm dacă există un parametru `next`
            next_url = request.GET.get('next')
            
            # 🔹 Ne asigurăm că `next_url` este sigur și nu e un URL extern
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts=request.get_host()):
                logger.debug(f"Redirecționare către {next_url}")  # DEBUG 3
                return JsonResponse({'success': True, 'redirect_url': next_url})
            
            logger.debug("Nicio destinație specificată, redirecționare către profil.")  # DEBUG 4
            return JsonResponse({'success': True, 'redirect_url': '/aplicatie_exemplu/profile/'})

    logger.debug("Cerere GET pentru pagina de login.")  # DEBUG 2
    form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})


@login_required
def profile(request):
    user = request.user  # Utilizatorul logat
    
    user_data = {
        "username": user.username,
        "first_name": user.first_name if user.first_name else "Necunoscut",
        "last_name": user.last_name if user.last_name else "Necunoscut",
        "email": user.email,
        "date_joined": user.date_joined.strftime("%Y-%m-%d"),
        "last_login": user.last_login.strftime("%Y-%m-%d %H:%M") if user.last_login else "Niciodată",
        "phone_number": user.phone_number if user.phone_number else "Nespecificat",
        "address": user.address if user.address else "Nespecificată",
        "date_of_birth": user.date_of_birth.strftime("%Y-%m-%d") if user.date_of_birth else "Nespecificată",
        "company_name": user.company_name if user.company_name else "Nespecificată",
        "is_staff": user.is_staff,
        "profile_picture": user.profile_picture.url if user.profile_picture else None,
    }

    return render(request, "profile.html", {"user_data": user_data})

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
    request.user.user_permissions.clear()  # Șterge permisiunile doar pentru sesiunea curentă
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
        
####lab 8 task 3

@login_required
def claim_offer(request):
    if request.method == "POST":
        try:
            content_type = ContentType.objects.get_for_model(CustomUser)
            permission = Permission.objects.get(codename="vizualizeaza_oferta", content_type=content_type)
            request.user.user_permissions.add(permission)
            return JsonResponse({"success": True})
        except Permission.DoesNotExist:
            return JsonResponse({"success": False, "error": "Permisiunea nu există."})
    return JsonResponse({"success": False, "error": "Metodă invalidă."})

@login_required
def oferta(request):
    if not request.user.has_perm('aplicatie_exemplu.vizualizeaza_oferta'):
        return render(request, "403.html", {
            "titlu": "Eroare afisare oferta",
            "mesaj_personalizat": "Nu ai voie să vizualizezi oferta."
        }, status=403)

    # Obține o ofertă aleatorie din baza de date
    promotie_aleasa = Promotie.objects.order_by('?').first()

    if promotie_aleasa:
        context = {
            "titlu": "Oferta Specială 🔥",
            "nume_oferta": promotie_aleasa.nume,
            "discount": promotie_aleasa.discount,
            "descriere": promotie_aleasa.descriere,
            "data_expirare": promotie_aleasa.data_expirare.strftime("%d-%m-%Y")
        }
    else:
        context = {
            "titlu": "Oferta Specială 🔥",
            "nume_oferta": None,  # Fără ofertă
        }

    return render(request, 'oferta.html', context)


def home(request):
    return render(request, 'home.html')
