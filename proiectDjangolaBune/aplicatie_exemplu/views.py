from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Product
from .forms import ProductFilterForm
from .forms import ContactForm
from .forms import ProductForm
from .forms import CustomUserRegistrationForm
from .models import Category
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User 


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
            form.save()
            return redirect('login')  # Redirecționează către pagina de login după înregistrare
    else:
        form = CustomUserRegistrationForm()
    
    return render(request, 'register.html', {'form': form})

#task 3 lab 6
def custom_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            request.session['user_id'] = user.id
            request.session['username'] = user.username
            request.session['email'] = user.email
            request.session['first_name'] = user.first_name  # Dacă ai acest câmp
            request.session['last_name'] = user.last_name  # Dacă ai acest câmp
            request.session['is_staff'] = user.is_staff  # Dacă utilizatorul e admin

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