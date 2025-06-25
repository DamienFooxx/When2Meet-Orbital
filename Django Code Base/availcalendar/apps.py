from django.apps import AppConfig


class AvailcalendarConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "availcalendar"

    def ready(self):
        import accounts.signals
