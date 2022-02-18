from django.apps import AppConfig


class EmailresetappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'EmailResetApp'
    
    def ready(self):
        import EmailResetApp.signals
