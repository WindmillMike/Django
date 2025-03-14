from django.urls import path
from .views import filter_products
from .views import contact_view
from .views import add_product
from .views import register
from .views import custom_login, custom_logout, profile, change_password
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

def dashboard(request):
    return render(request, 'dashboard.html')

from . import views
urlpatterns = [
	path("", views.index, name="index"),
	path('filter-products/', filter_products, name='filter_products'),
	path('contact/', contact_view, name='contact'),
    path('add-product/', add_product, name='add_product'),
    path('register/', register, name='register'),
    path('login/', custom_login, name='login'),
    path('logout/', custom_logout, name='logout'),
    path('profile/', profile, name='profile'),
    path('change-password/', change_password, name='change_password'),
]
