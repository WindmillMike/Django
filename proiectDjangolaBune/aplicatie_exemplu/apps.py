from django.apps import AppConfig

class AplicatieExempluConfig(AppConfig):  # Înlocuiește cu numele real al aplicației tale
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'aplicatie_exemplu'  # Schimbă cu numele aplicației tale

    def ready(self):
        import aplicatie_exemplu.signals  # Importă signals pentru a funcționa corect
