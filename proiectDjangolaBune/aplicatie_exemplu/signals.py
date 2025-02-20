from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Product
from django.contrib.auth.signals import user_logged_out
from aplicatie_exemplu.models import CustomUser
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.contrib.auth import get_user_model




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
    
####lab 8 task 3
@receiver(post_migrate)
def create_offer_permission(sender, **kwargs):
    if sender.name == 'aplicatie_exemplu':  # Asigură-te că rulezi în aplicația ta
        content_type = ContentType.objects.get_for_model(CustomUser)
        Permission.objects.get_or_create(
            codename="vizualizeaza_oferta",
            name="Poate vizualiza oferta",
            content_type=content_type,
        )
        
        
@receiver(user_logged_out)
def remove_offer_permission(sender, request, user, **kwargs):
    perm = Permission.objects.get(codename="vizualizeaza_oferta")
    user.user_permissions.remove(perm)
    

User = get_user_model()

@receiver(post_save, sender=User)
def make_superuser_if_staff(sender, instance, **kwargs):

    if instance.is_staff and not instance.is_superuser:
        instance.is_superuser = True
        instance.save(update_fields=["is_superuser"])  # Salvăm doar acest câmp
