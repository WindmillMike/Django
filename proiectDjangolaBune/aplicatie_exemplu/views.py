from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Product
from .forms import ProductFilterForm
from .forms import ContactForm
from .forms import ProductForm
from .forms import CustomUserRegistrationForm
from .models import Category
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from .forms import send_confirmation_email
from .models import CustomUser
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib import messages


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
    """ Înregistrarea utilizatorului și verificarea email-ului înainte de trimiterea confirmării. """
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data['email']
            
            if get_user_model().objects.filter(email=email).exists():
                form.add_error('email', 'Acest email este deja folosit.')
            else:
                user = form.save()
                send_confirmation_email(user)
                return redirect('email_confirmation_sent') 
    else:
        form = CustomUserRegistrationForm()

    return render(request, 'register.html', {'form': form})

def confirm_email(request, cod):
    """ Confirmă email-ul utilizatorului. """
    try:
        user = CustomUser.objects.get(cod=cod)
        print(f"User găsit: {user.username}, Email confirmat: {user.email_confirmat}")

        if user.email_confirmat:
            messages.info(request, "Email-ul este deja confirmat.")
        else:
            user.email_confirmat = True
            user.cod = None 
            user.save()
            print("Email confirmat cu succes!")
            messages.success(request, "Email-ul a fost confirmat cu succes!")

        return render(request, 'email_confirmed.html')

    except CustomUser.DoesNotExist:
        print("Cod invalid sau email deja confirmat.")
        messages.error(request, "Cod invalid sau email deja confirmat.")
        return render(request, 'email_invalid.html')

#task 3 lab 6
def custom_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()

            if not user.email_confirmat:
                messages.error(request, "Trebuie să îți confirmi email-ul înainte de a te autentifica.")
                return redirect('login')

            login(request, user)

            request.session['user_id'] = user.id
            request.session['username'] = user.username
            request.session['email'] = user.email
            request.session['first_name'] = user.first_name  
            request.session['last_name'] = user.last_name  
            request.session['is_staff'] = user.is_staff  

            remember_me = request.POST.get('remember_me', False)
            if remember_me:
                request.session.set_expiry(86400)  # Sesiunea expiră în 1 zi
            else:
                request.session.set_expiry(0)  # Expiră la închiderea browserului

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

#########lab 7

def send_confirmation_email(user):
    """ Trimite email-ul de confirmare folosind un template HTML. """
    
    site_url = "http://192.168.0.115:8000"  # Schimbă cu IP-ul local al laptopului!

    confirmation_link = f"{site_url}/aplicatie_exemplu/confirma_mail/{user.cod}/"

    email_content = render_to_string('email_confirmation_template.html', {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'username': user.username,
        'confirmation_link': confirmation_link
    })

    subject = "Confirmă-ți email-ul"
    
    email = EmailMessage(subject, email_content, settings.DEFAULT_FROM_EMAIL, [user.email])
    email.content_subtype = "html"
    email.send()