from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Product, Promotie
from datetime import datetime

class ProductSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Product.objects.all()

    def location(self, obj):
        return reverse('produs_detail', kwargs={'nume_produs': obj.name})

class PromotieSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return Promotie.objects.filter(data_expirare__gte=datetime.now())

    def location(self, obj):
        return reverse('lista_promotii')

class StaticViewSitemap(Sitemap):
    priority = 1.0
    changefreq = "monthly"

    def items(self):
        return ['index', 'home', 'contact', 'lista_produse', 'lista_promotii', 'oferta']

    def location(self, item):
        return reverse(item)
