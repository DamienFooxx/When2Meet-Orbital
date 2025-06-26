from django.urls import path, include
from rest_framework.routers import DefaultRouter
from availcalendar.views import (
    GoogleCalendarSyncView,
    TimeSlotViewSet,
    CalendarEntryViewSet,
    ManualAvailabilityViewSet,
    ReminderViewSet,
)

router = DefaultRouter()
router.register(r"timeslots", TimeSlotViewSet, basename="timeslot")
router.register(r"calendar-entries", CalendarEntryViewSet, basename="calendar-entry")
router.register(
    r"manual-availability", ManualAvailabilityViewSet, basename="manual-availability"
)
router.register(r"reminders", ReminderViewSet, basename="reminder")

urlpatterns = [
    path("sync/google/", GoogleCalendarSyncView.as_view(), name="calendar-google-sync"),
    path("", include(router.urls)),
]
