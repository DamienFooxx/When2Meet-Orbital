from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

urlpatterns = [
    path(
        "", lambda request: HttpResponse("When2Meet Backend is running!"), name="home"
    ),
    path("admin/", admin.site.urls),
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
