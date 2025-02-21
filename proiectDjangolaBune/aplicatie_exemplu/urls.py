from django.urls import path
from django.contrib.sitemaps.views import sitemap
from django.shortcuts import render
from .views import (
    filter_products, contact_view, add_product, register, confirm_email,
    creare_promotie, lista_promotii, lista_produse, produs_detail,
    custom_login, custom_logout, profile, change_password,
    pagina_protejata, claim_offer, oferta, index
)
from .sitemap import ProductSitemap, PromotieSitemap, StaticViewSitemap  # Eliminat OrderSitemap

# Definirea sitemap-urilor pentru diverse modele și pagini statice
sitemaps = {
    'products': ProductSitemap(),
    'promotions': PromotieSitemap(),
    'static': StaticViewSitemap(),
}

# Funcție pentru dashboard
def dashboard(request):
    return render(request, 'dashboard.html')

# Definirea URL-urilor
urlpatterns = [
    path("", index, name="index"),
    path("filter-products/", filter_products, name="filter_products"),
    path("contact/", contact_view, name="contact"),
    path("add-product/", add_product, name="add_product"),
    path("register/", register, name="register"),
    path("login/", custom_login, name="login"),
    path("logout/", custom_logout, name="logout"),
    path("profile/", profile, name="profile"),
    path("change-password/", change_password, name="change_password"),
    path("confirma_mail/<str:cod>/", confirm_email, name="confirm_email"),
    path("promotii/", creare_promotie, name="creare_promotie"),
    path("lista-promotii/", lista_promotii, name="lista_promotii"),
    path("produs/<str:nume_produs>/", produs_detail, name="produs_detail"),
    path("produse/", lista_produse, name="lista_produse"),
    path("pagina-protejata/", pagina_protejata, name="pagina_protejata"),
    path("claim_offer/", claim_offer, name="claim_offer"),
    path("oferta/", oferta, name="oferta"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
]
