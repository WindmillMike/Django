from celery import shared_task
from django.utils.timezone import now, timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import Product, Promotie

CustomUser = get_user_model()

#  Ștergerea utilizatorilor care nu și-au confirmat emailul la fiecare 2 minute
@shared_task
def sterge_utilizatori_neconfirmati():
    K = 2  # Minute
    limita = now() - timedelta(minutes=K)
    sterguti = CustomUser.objects.filter(email_confirmat=False, date_joined__lt=limita).delete()
    return f"{sterguti[0]} utilizatori neconfirmați au fost șterși."

# Trimiterea unui newsletter în fiecare luni la ora 8:00 AM către utilizatorii mai vechi de 30 minute
@shared_task
def trimite_newsletter():
    Z = 0  # Luni (0=Luni, 1=Marți, ..., 6=Duminică)
    O = 8  # Ora 8:00 AM
    X = 30  # Minute
    limita = now() - timedelta(minutes=X)
    utilizatori = CustomUser.objects.filter(date_joined__lt=limita, newsletter_subscription=True)
    
    for user in utilizatori:
        send_mail(
            subject="Newsletter Săptămânal",
            message="Acesta este newsletter-ul nostru săptămânal!",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email]
        )
    
    return f"Newsletter trimis la {utilizatori.count()} utilizatori."

#Task la fiecare 5 minute pentru verificarea produselor cu stoc zero și alertarea adminilor
@shared_task
def verifica_stoc_zero():
    M = 5  # Minute
    produse_fara_stoc = Product.objects.filter(stock_quantity=0)
    
    if produse_fara_stoc.exists():
        send_mail(
            subject="Produse fără stoc!",
            message="Există produse care au rămas fără stoc.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['admin@example.com']
        )

    return f"{produse_fara_stoc.count()} produse fără stoc identificate."

# Task zilnic la ora 20:00 pentru reducerea automată a prețurilor promoțiilor care expiră curând
@shared_task
def aplica_reduceri():
    Z2 = 6  # Duminică
    O2 = 20  # Ora 20:00
    promotii = Promotie.objects.filter(data_expirare__lte=now() + timedelta(days=1))
    
    for promotie in promotii:
        for produs in promotie.categorie.products.all():
            produs.price *= 0.9  # Aplică o reducere de 10%
            produs.save()

    return f"Reduceri aplicate pentru {promotii.count()} promoții care expiră curând."
