from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Product
from .forms import ProductFilterForm
from .forms import ContactForm
from .forms import ProductForm

def index(request):
	return HttpResponse("Primul raspuns")

def filter_products(request):
    print("Funcția filter_products a fost apelată!")
    form = ProductFilterForm(request.GET)
    products = Product.objects.all()
    
    if form.is_valid():
        if form.cleaned_data.get('name'):
            products = products.filter(name__icontains=form.cleaned_data['name'])
        if form.cleaned_data.get('category'):
            products = products.filter(category=form.cleaned_data['category'])
        if form.cleaned_data.get('min_price'):
            products = products.filter(price__gte=form.cleaned_data['min_price'])
        if form.cleaned_data.get('max_price'):
            products = products.filter(price__lte=form.cleaned_data['max_price'])
        if form.cleaned_data.get('min_stock'):
            products = products.filter(stock_quantity__gte=form.cleaned_data['min_stock'])
        if form.cleaned_data.get('max_stock'):
            products = products.filter(stock_quantity__lte=form.cleaned_data['max_stock'])

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  #Bonus
        data = list(products.values('name', 'price', 'stock_quantity', 'category__name'))
        return JsonResponse({'products': data})
    
    return render(request, 'product_filter.html', {'form': form, 'products': products})

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