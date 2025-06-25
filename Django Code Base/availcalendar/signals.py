from allauth.account.signals import social_account_added
from django.dispatch import receiver
from availcalendar.services import sync_google_integration


@receiver(social_account_added)
def on_social_account_added(request, sociallogin, **kwargs):
    if sociallogin.account.provider == "google":
        sync_google_integration(request.user)
