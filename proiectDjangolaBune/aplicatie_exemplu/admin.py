from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Category, Product, Order, OrderProduct, Supplier, ProductSupplier
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

# Personalizare Admin Site - Schimbă titlurile afișate în panoul de administrare
admin.site.site_header = "Panou de Administrare - Magazin"  # Titlul principal al Admin Panel
admin.site.site_title = "Admin Magazin"  # Titlul paginii în browser
admin.site.index_title = "Gestionare Produse și Comenzi"  # Titlul indexului din Admin

# Definirea unui filtru personalizat pentru cantitatea de stoc
class StockQuantityFilter(admin.SimpleListFilter):
    title = _('Stock Quantity')  # Titlul filtrului
    parameter_name = 'stock_quantity'  # Numele parametrului de filtrare

    def lookups(self, request, model_admin):
        # Definirea opțiunilor de filtrare
        return [
            ('low', _('Low Stock (<10)')),
            ('medium', _('Medium Stock (10-50)')),
            ('high', _('High Stock (>50)')),
        ]

    def queryset(self, request, queryset):
        # Aplică filtrul în funcție de selecție
        if self.value() == 'low':
            return queryset.filter(stock_quantity__lt=10)
        if self.value() == 'medium':
            return queryset.filter(stock_quantity__gte=10, stock_quantity__lte=50)
        if self.value() == 'high':
            return queryset.filter(stock_quantity__gt=50)
        return queryset

# Definirea unui filtru personalizat pentru preț
class PriceRangeFilter(admin.SimpleListFilter):
    title = _('Price Range')  # Titlul filtrului afișat în Admin
    parameter_name = 'price_range'  # Numele parametrului de filtrare

    def lookups(self, request, model_admin):
        # Definește intervalele de preț
        return [
            ('low', _('Low (< 50)')),
            ('medium', _('Medium (50-200)')),
            ('high', _('High (> 200)')),
        ]

    def queryset(self, request, queryset):
        # Aplică filtrarea bazată pe intervale de preț
        if self.value() == 'low':
            return queryset.filter(price__lt=50)
        if self.value() == 'medium':
            return queryset.filter(price__gte=50, price__lte=200)
        if self.value() == 'high':
            return queryset.filter(price__gt=200)
        return queryset

# Configurarea tabelului Product în Admin Panel
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'stock_quantity', 'category']  # Coloanele afișate în lista de produse
    search_fields = ['name']  # Permite căutarea după numele produsului
    list_filter = [
        'category',  # Filtru pentru categorie (ForeignKey)
        PriceRangeFilter,  # Filtru pentru preț bazat pe intervale definite
        StockQuantityFilter  # Filtru definit pentru cantitatea de stoc
    ]
    list_per_page = 10  # Paginare - 10 produse pe pagină

    # Organizarea câmpurilor în două secțiuni pentru o mai bună organizare
    fieldsets = (
        ('Informații generale', {
            'fields': ('name', 'description', 'category')
        }),
        ('Detalii suplimentare', {
            'fields': ('price', 'stock_quantity')
        }),
    )

# Înregistrarea modelului Product cu setările personalizate
admin.site.register(Product, ProductAdmin)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ['name']  # Permite căutarea categoriilor după nume

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'order_date', 'total_price', 'status']  # Coloanele afișate în Admin
    search_fields = ['status']  # Permite căutarea după status
    list_filter = ['status', 'order_date']  # Adaugă filtre pentru status și dată

@admin.register(OrderProduct)
class OrderProductAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'unit_price']  # Coloanele afișate
    search_fields = ['product__name']  # Căutare după numele produsului asociat

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_info']  # Coloanele afișate pentru furnizori
    search_fields = ['name']  # Căutare după numele furnizorului

@admin.register(ProductSupplier)
class ProductSupplierAdmin(admin.ModelAdmin):
    list_display = ['product', 'supplier', 'supply_date', 'quantity_supplied']  # Coloane afișate
    search_fields = ['product__name']  # Căutare după numele produsului

#lab6 task1
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        ("Informații suplimentare", {"fields": ("phone_number", "date_of_birth", "address", "profile_picture", "newsletter_subscription", "company_name")}),
    )

admin.site.register(CustomUser, CustomUserAdmin)