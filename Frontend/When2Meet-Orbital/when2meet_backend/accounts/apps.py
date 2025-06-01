from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """
    AppConfig for the accounts app. Connects signals on app ready.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        import accounts.signals