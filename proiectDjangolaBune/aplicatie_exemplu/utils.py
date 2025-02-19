from django.core.mail import send_mass_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import CustomUser

from django.core.mail import send_mass_mail
from django.conf import settings

def trimite_mail_promotii(utilizatori_promo, promotie):
    emailuri = []

    for categorie, utilizatori in utilizatori_promo.items():
        for user_id in utilizatori:
            # Obținem utilizatorul și emailul său
            user = CustomUser.objects.get(id=user_id)

            # Subiectul și conținutul emailului
            subject = f"Promoție Specială: {promotie.nume}"
            message = f"""
            Bună {user.username},

            Avem o ofertă specială pentru categoria {categorie}!

            {promotie.descriere}

            Această promoție este valabilă până pe {promotie.data_expirare.strftime('%d/%m/%Y')}.

            Profită acum!

            Echipa Magazinului
            """
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [user.email]

            emailuri.append((subject, message, from_email, recipient_list))

    if emailuri:
        send_mass_mail(emailuri, fail_silently=False)

