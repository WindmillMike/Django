from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Product

@receiver(post_migrate)
def create_admin_products_group(sender, **kwargs):
    # Creăm sau obținem grupul
    group, created = Group.objects.get_or_create(name="Administratori_produse")

    # Obținem toate permisiunile asociate modelului `Product`
    content_type = ContentType.objects.get_for_model(Product)
    permissions = Permission.objects.filter(content_type=content_type)

    # Atribuim toate permisiunile grupului
    group.permissions.set(permissions)

    print("Grupul 'Administratori_produse' a fost creat sau există deja și are permisiuni asupra produselor.")