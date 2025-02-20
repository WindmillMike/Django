from django.urls import path
from .views import filter_products
from .views import contact_view
from .views import add_product
from .views import register
from .views import confirm_email
from .views import creare_promotie
from .views import lista_promotii
from .views import lista_produse, produs_detail
from .views import custom_login, custom_logout, profile, change_password
from .views import pagina_protejata
from .views import claim_offer, oferta
from .views import home
from django.shortcuts import render

def dashboard(request):
    return render(request, 'dashboard.html')

from . import views
urlpatterns = [
	path("", views.index, name="index"),
    path('', home, name='home'), 
	path('filter-products/', filter_products, name='filter_products'),
	path('contact/', contact_view, name='contact'),
    path('add-product/', add_product, name='add_product'),
    path('register/', register, name='register'),
    path('login/', custom_login, name='login'),
    path('logout/', custom_logout, name='logout'),
    path('profile/', profile, name='profile'),
    path('change-password/', change_password, name='change_password'),
    path('confirma_mail/<str:cod>/', confirm_email, name='confirm_email'),
    path('promotii/', creare_promotie, name='creare_promotie'),
    path('lista-promotii/', lista_promotii, name='lista_promotii'),
    path('produs/<str:nume_produs>/', produs_detail, name='produs_detail'),
    path('produse/', lista_produse, name='lista_produse'),
    path('pagina-protejata/', pagina_protejata, name='pagina_protejata'),
    path('claim_offer/', claim_offer, name='claim_offer'),
    path('oferta/', oferta, name='oferta'),
]
