from django.urls import path, include
from rest_framework.routers import DefaultRouter
from availcalendar.views import (
    GoogleCalendarSyncView,
    TimeSlotViewSet,
    CalendarEntryViewSet,
    CalendarIntegrationViewSet,
    ManualAvailabilityViewSet,
    ReminderViewSet,
    month_availability,
    submit_availability,
    get_availability_for_event,
)

router = DefaultRouter()
router.register(r"timeslots", TimeSlotViewSet, basename="timeslot")
router.register(r"calendar-entries", CalendarEntryViewSet, basename="calendar-entry")
router.register(r"calendar-integrations", CalendarIntegrationViewSet, basename="calendar-integration")
router.register(
    r"manual-availability", ManualAvailabilityViewSet, basename="manual-availability"
)
router.register(r"reminders", ReminderViewSet, basename="reminder")

urlpatterns = [
    path(
        'sync/google/',
        GoogleCalendarSyncView.as_view(),
        name='calendar-google-sync'
    ),
    path('month/', month_availability, name='month-availability'),
    path('submit-availability/', submit_availability, name='submit-availability'),
    path('event/<int:event_id>/availability/', get_availability_for_event, name='get-availability'),
    path('', include(router.urls)),
]
