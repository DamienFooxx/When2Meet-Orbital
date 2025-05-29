from django.urls import path, include
from.views import GoogleLogin

urlpatterns = [
    path('auth/', include('dj_rest_auth.urls')),  # login/logout/password reset
    path('auth/registration/', include('dj_rest_auth.registration.urls')),  # signup
    path('auth/google/', GoogleLogin.as_view(), name='google_login'),  # Google OAuth
]