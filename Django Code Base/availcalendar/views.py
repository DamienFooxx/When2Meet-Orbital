from django.db.models import Q
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .tasks import sync_google_calendar_task, get_google_token, fetch_google_busy_slots
from .models import Event, TimeSlot, CalendarEntry, ManualAvailability, Reminder
from .serializers import (
    EventSerializer,
    TimeSlotSerializer,
    ManualAvailabilitySerializer,
    CalendarIntegrationSerializer,
    CalendarEntrySerializer,
    ReminderSerializer,
)
from accounts.serializers import FreeBusyRequestSerializer


class EventViewSet(viewsets.ModelViewSet):
    """
    CRUD for calendar Events. Only events the user created or participates in.
    """
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        profile = self.request.user.profile
        return Event.objects.filter(
            Q(participants=profile) | Q(creator=profile)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user.profile)


class TimeSlotViewSet(viewsets.ModelViewSet):
    """
    CRUD for TimeSlots. Only timeslots for events the user is in.
    """
    serializer_class = TimeSlotSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        profile = self.request.user.profile
        return TimeSlot.objects.filter(
            Q(event__participants=profile) | Q(event__creator=profile)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user.profile)


class CalendarEntryViewSet(viewsets.ModelViewSet):
    """
    CRUD for CalendarEntry (token records). Scoped to the user's entries.
    """
    serializer_class = CalendarEntrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CalendarEntry.objects.filter(user=self.request.user.profile)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user.profile)


class ManualAvailabilityViewSet(viewsets.ModelViewSet):
    """
    CRUD for ManualAvailability. Scoped to the user's manual slots.
    """
    serializer_class = ManualAvailabilitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ManualAvailability.objects.filter(user=self.request.user.profile)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user.profile)


class ReminderViewSet(viewsets.ModelViewSet):
    """
    CRUD for Reminders. Scoped to the user's reminders.
    """
    serializer_class = ReminderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Reminder.objects.filter(user=self.request.user.profile)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user.profile)


class GoogleCalendarSyncView(APIView):
    """
    GET    → fetch busy slots from Google Calendar (preview)
    PUT    → enqueue async task to sync busy slots into TimeSlot
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = FreeBusyRequestSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        start = serializer.validated_data['start']
        end = serializer.validated_data['end']
        calendars = serializer.validated_data.get('calendars', ['primary'])

        token = get_google_token(request.user.id)
        if not token:
            return Response({"error": "Google account not connected"}, status=status.HTTP_400_BAD_REQUEST)

        busy, error = fetch_google_busy_slots(start, end, token, calendars)
        if error:
            return Response(
                {"error": "Failed to fetch from Google", "details": error},
                status=status.HTTP_502_BAD_GATEWAY
            )

        return Response({"busy": busy}, status=status.HTTP_200_OK)

    def put(self, request):
        serializer = FreeBusyRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        start = serializer.validated_data['start']
        end = serializer.validated_data['end']
        calendars = serializer.validated_data.get('calendars', ['primary'])

        sync_google_calendar_task.delay(
            user_id=request.user.id,
            start_iso=start.isoformat(),
            end_iso=end.isoformat(),
            calendar_ids=calendars
        )
        return Response(
            {"message": "Calendar synchronization initiated."},
            status=status.HTTP_202_ACCEPTED
        )
