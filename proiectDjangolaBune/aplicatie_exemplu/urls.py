from django.urls import path
from .views import filter_products
from .views import contact_view
from .views import add_product
from .views import register, confirm_email
from .views import custom_login, custom_logout, profile, change_password
from django.shortcuts import render

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
    path('confirma_mail/<str:cod>/', confirm_email, name='confirm_email'),
    path('email-confirmation-sent/', lambda request: render(request, 'email_confirmation_sent.html'), name='email_confirmation_sent'),
]
