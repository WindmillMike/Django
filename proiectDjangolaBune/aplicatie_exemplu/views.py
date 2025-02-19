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
from django.core.mail import send_mass_mail
from .utils import trimite_mail_promotii


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

def add_product(request):
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
def register(request):
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.cod = str(uuid.uuid4().hex)[:20] 
            user.email_confirmat = False  
            user.save()
            
            confirmation_link = request.build_absolute_uri(reverse('confirm_email', args=[user.cod]))

            email_body = render_to_string('email_confirmation.html', {
                'user': user,
                'confirmation_link': confirmation_link
            })

            send_mail(
                subject="Confirmare cont - Magazin",
                message='',  # Lăsăm mesajul gol pentru că trimitem HTML
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=email_body
            )

            messages.success(request, "Cont creat cu succes! Verifică e-mailul pentru confirmare.")
            return redirect('login')  
    
    else:
        form = CustomUserRegistrationForm()
    
    return render(request, 'register.html', {'form': form})


#task 3 lab 6
def custom_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is None:
                messages.error(request, "Autentificare eșuată. Verifică credențialele.")
                return redirect('login')

            if not user.email_confirmat:  # ✅ Verificăm confirmarea e-mailului
                messages.error(request, "Trebuie să-ți confirmi e-mailul înainte de a te autentifica.")
                return redirect('login')

            # ✅ Dacă utilizatorul este confirmat, îl logăm și setăm sesiunea
            login(request, user)
            request.session['user_id'] = user.id
            request.session['username'] = user.username
            request.session['email'] = user.email
            request.session['first_name'] = user.first_name
            request.session['last_name'] = user.last_name
            request.session['is_staff'] = user.is_staff

            remember_me = request.POST.get('remember_me', False)
            request.session.set_expiry(86400 if remember_me else 0)

            return redirect('profile')

    else:
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
    user = get_object_or_404(CustomUser, cod=cod)  

    if not user.email_confirmat:
        user.email_confirmat = True 
        user.cod = None  
        user.save()
        messages.success(request, "E-mail confirmat cu succes! Acum te poți autentifica.")
    else:
        messages.info(request, "E-mailul a fost deja confirmat.")

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
    K = 3  # ✅ Minim K vizualizări pentru a primi promoția

    if request.method == 'POST':
        form = PromotieForm(request.POST)
        if form.is_valid():
            promotie = form.save(commit=False)
            promotie.save()
            form.save_m2m()  # ✅ Salvăm categoriile promoției

            categorii_selectate = form.cleaned_data['categorii']

            # ✅ Selectăm utilizatorii care au vizualizat produse din categoriile promoției de minim K ori
            utilizatori_promo = {}
            for categorie in categorii_selectate:
                utilizatori = Vizualizare.objects.filter(
                    produs__category=categorie
                ).values('utilizator').annotate(numar_vizualizari=models.Count('id')).filter(numar_vizualizari__gte=K)

                utilizatori_promo[categorie.name] = [u['utilizator'] for u in utilizatori]

            # ✅ Trimitere e-mailuri cu `send_mass_mail()`
            trimite_mail_promotii(utilizatori_promo, promotie)
            messages.success(request, "Promoția a fost creată și e-mailurile au fost trimise!")
            return redirect('creare_promotie')  # ✅ Redirecționare la aceeași pagină pentru o nouă promoție

    else:
        form = PromotieForm()
    
    return render(request, 'promotii.html', {'form': form})

def lista_promotii(request):
    promotii = Promotie.objects.all()
    return render(request, 'lista_promotii.html', {'promotii': promotii})


from django.shortcuts import render, get_object_or_404
from django.db.models import F
from django.utils.timezone import now
from .models import Product, Vizualizare

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