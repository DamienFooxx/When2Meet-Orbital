from django.urls import path, include
from .views import GoogleLogin
from .views import GoogleCalendarFreeBusyView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter

"""
accounts/urls.py

Routes authentication endpoints for the accounts app, including Google OAuth.
"""
'''
class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
'''
urlpatterns = [
    path('auth/', include('dj_rest_auth.urls')),  # login/logout/password reset
    path('auth/registration/', include('dj_rest_auth.registration.urls')),  # signup
    path('auth/google/', GoogleLogin.as_view(), name='google_login'),  # Google OAuth login endpoint
    path('auth/', include('allauth.socialaccount.urls')),
    path('google-calendar/freebusy/', GoogleCalendarFreeBusyView.as_view(), name = 'google_calendar_freebusy'),
]