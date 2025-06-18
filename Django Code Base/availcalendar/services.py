from allauth.socialaccount.models import SocialAccount, SocialToken
from django.utils import timezone
from accounts.models import Profile
from .models import CalendarIntegration

def sync_google_integration(user):
    profile = Profile.objects.get(user=user)
    try:
        soc_acc = SocialAccount.objects.get(user=user, provider='google')
        soc_tok = SocialToken.objects.get(account=soc_acc)
    except (SocialAccount.DoesNotExist, SocialToken.DoesNotExist):
        raise RuntimeError("Google account not connected")

    external_id   = soc_acc.uid
    access_token  = soc_tok.token
    refresh_token = soc_tok.token_secret or soc_acc.extra_data.get('refresh_token')
    token_expiry  = soc_tok.expires_at or timezone.now()

    CalendarIntegration.objects.update_or_create(
        provider='google',
        user_id=profile,
        defaults={
            'external_id':  external_id,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_expiry': token_expiry,
        }
    )
