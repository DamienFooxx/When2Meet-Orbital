from django.urls import path
from .views import GoogleCalendarSyncView

urlpatterns = [
    path(
        'sync/google/',
        GoogleCalendarSyncView.as_view(),
        name='calendar-google-sync'
    ),
]
