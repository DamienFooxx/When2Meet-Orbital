from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialApp
from django.conf import settings
import os


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter to handle multiple Google OAuth applications
    by selecting the one that matches the environment's CLIENT_ID.
    """

    def get_app(self, request, provider, client_id=None):
        """
        Override to select the correct Google OAuth app based on CLIENT_ID from environment.
        """
        if provider == 'google' and not client_id:
            # Use the CLIENT_ID from environment variables to select the correct app
            expected_client_id = os.getenv("GOOGLE_CLIENT_ID")
            if expected_client_id:
                try:
                    app = SocialApp.objects.get(
                        provider=provider,
                        client_id=expected_client_id
                    )
                    return app
                except SocialApp.DoesNotExist:
                    pass
                except SocialApp.MultipleObjectsReturned:
                    # If there are still multiple, get the first one with matching client_id
                    app = SocialApp.objects.filter(
                        provider=provider,
                        client_id=expected_client_id
                    ).first()
                    return app
        
        # Fall back to default behavior
        return super().get_app(request, provider, client_id)
