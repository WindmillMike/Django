from django.urls import path
from .views import filter_products
from .views import contact_view
from .views import add_product

from . import views
urlpatterns = [
	path("", views.index, name="index"),
	path('filter-products/', filter_products, name='filter_products'),
	path('contact/', contact_view, name='contact'),
    path('add-product/', add_product, name='add_product'),
]
