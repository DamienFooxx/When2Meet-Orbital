from django.apps import AppConfig


class AvailcalendarConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'availcalendar'

class AccountsConfig(AppConfig):
    name = 'accounts'

    def ready(self):
        import accounts.signals
