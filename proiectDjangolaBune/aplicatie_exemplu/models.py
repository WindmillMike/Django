from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils.timezone import now

# laboratorul 3 taskurile 2 si 3
class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    stock_quantity = models.IntegerField()
    

    def __str__(self):
        return self.name
    
    def get_final_price(self, discount_percentage, tax_percentage):
        discounted_price = self.price - (self.price * (discount_percentage / 100))
        final_price = discounted_price + (discounted_price * (tax_percentage / 100))
        return round(final_price, 2) 

class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled')
    ]
    order_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)

    def __str__(self):
        return f"Order {self.id} - {self.status}"

class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_products')
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"

class Supplier(models.Model):
    name = models.CharField(max_length=255)
    contact_info = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class ProductSupplier(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='suppliers')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='products')
    supply_date = models.DateField()
    quantity_supplied = models.IntegerField()

    def __str__(self):
        return f"{self.supplier.name} supplies {self.product.name}"
#######################################################################
#######
class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name="Număr de telefon", unique=True)
    date_of_birth = models.DateField(blank=True, null=True, verbose_name="Data nașterii")
    address = models.TextField(blank=True, null=True, verbose_name="Adresă")
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True, verbose_name="Poză de profil")
    newsletter_subscription = models.BooleanField(default=False, verbose_name="Abonat la newsletter")
    company_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nume companie")
    
    cod = models.CharField(max_length=100, blank=True, null=True, unique=True)
    email_confirmat = models.BooleanField(default=False)

    class Meta:
        db_table = "custom_user"

    def __str__(self):
        return self.username


###lab 7 task 2

class Vizualizare(models.Model):
    utilizator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    produs = models.ForeignKey('Product', on_delete=models.CASCADE)
    data_vizualizare = models.DateTimeField(default=now)
    numar_vizualizari = models.IntegerField(default=1) 

    class Meta:
        verbose_name = "Vizualizare"
        verbose_name_plural = "Views" 
        ordering = ['-data_vizualizare']  # Cele mai recente primele
        
    def __str__(self):
        return f"{self.utilizator.username} a vizualizat {self.produs.name}"
        

class Promotie(models.Model):
    nume = models.CharField(max_length=255)
    data_creare = models.DateTimeField(auto_now_add=True)
    data_expirare = models.DateTimeField()
    categorie = models.ManyToManyField('Category')  # Promoția e valabilă pentru mai multe categorii
    discount = models.DecimalField(max_digits=5, decimal_places=2)  # Discount în procente
    descriere = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Promotion"
        verbose_name_plural = "Promotions"  # Plural corect

    def __str__(self):
        return f"{self.nume} (Expiră: {self.data_expirare})"
    

###lab7 task 3
class FailedLoginAttempt(models.Model):
    username = models.CharField(max_length=150)
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} - {self.ip_address} - {self.timestamp}"