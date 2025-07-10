from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from .views import health_check
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="When2Meet API",
      default_version='v1',
      description="API documentation for When2Meet scheduling app",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@when2meet.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path(
        "", lambda request: HttpResponse("When2Meet Backend is running!"), name="home"
    ),
    path("admin/", admin.site.urls),
    path('api/health/', health_check, name='health_check'),
    
    # Swagger documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/schema/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    
    # authentication-related
    path('api/auth/', include('dj_rest_auth.urls')),
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),
    # App related
    path('api/', include('accounts.urls')),
    path('api/', include('groups.urls')),
    path('api/', include('availcalendar.urls')),
    path('api/', include('events.urls')),
    path('api/', include('smartScheduling.urls')),
]
