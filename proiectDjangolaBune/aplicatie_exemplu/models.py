from django.db import models
from django.contrib.auth.models import AbstractUser

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

    class Meta:
        db_table = "custom_user"

    def __str__(self):
        return self.username