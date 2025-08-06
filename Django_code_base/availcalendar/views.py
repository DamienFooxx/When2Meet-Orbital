from django.db.models import Q
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from calendar import monthrange
from datetime import date, timedelta
from availcalendar.tasks import sync_google_calendar_task, get_google_token, fetch_google_busy_slots
from availcalendar.models import TimeSlot, CalendarEntry, CalendarIntegration, ManualAvailability, Reminder
from events.models import Event
from availcalendar.serializers import (
    TimeSlotSerializer,
    ManualAvailabilitySerializer,
    CalendarIntegrationSerializer,
    CalendarEntrySerializer,
    ReminderSerializer,
)
from accounts.serializers import FreeBusyRequestSerializer
from groups.models import GroupMembership


class TimeSlotViewSet(viewsets.ModelViewSet):
    """
    CRUD for TimeSlots. Only timeslots for events the user is in.
    """

    serializer_class = TimeSlotSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        profile = self.request.user.profile
        return TimeSlot.objects.filter(
            Q(event_id__participants=profile) | Q(event_id__creator=profile)
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
        return CalendarEntry.objects.filter(user_id=self.request.user.profile)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user.profile)


class CalendarIntegrationViewSet(viewsets.ModelViewSet):
    """
    CRUD for CalendarIntegration to check if Google Calendar is successfully connected
    """

    serializer_class = CalendarIntegrationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CalendarIntegration.objects.filter(user=self.request.user.profile)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user.profile)

    def list(self, request, *args, **kwargs):
        """Override list to return connection status"""
        exists = CalendarIntegration.objects.filter(
            provider="google", user=request.user.profile
        ).exists()
        return Response({"connected": exists})


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
        return Reminder.objects.filter(user_id=self.request.user.profile)

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user.profile)


class GoogleCalendarSyncView(APIView):
    """
    GET    → fetch busy slots from Google Calendar (preview)
    PUT    → enqueue async task to sync busy slots into TimeSlot
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = FreeBusyRequestSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        start = serializer.validated_data["start"]
        end = serializer.validated_data["end"]
        calendars = serializer.validated_data.get("calendars", ["primary"])

        token = get_google_token(request.user.id)
        if not token:
            return Response(
                {"error": "Google account not connected"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        busy, error = fetch_google_busy_slots(start, end, token, calendars)
        if error:
            return Response(
                {"error": "Failed to fetch from Google", "details": error},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response({"busy": busy}, status=status.HTTP_200_OK)

    def put(self, request):
        serializer = FreeBusyRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        start = serializer.validated_data["start"]
        end = serializer.validated_data["end"]
        calendars = serializer.validated_data.get("calendars", ["primary"])

        sync_google_calendar_task.delay(
            user_id=request.user.id,
            start_iso=start.isoformat(),
            end_iso=end.isoformat(),
            calendar_ids=calendars,
        )
        return Response(
            {"message": "Calendar synchronization initiated."},
            status=status.HTTP_202_ACCEPTED,
        )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def month_availability(request):
    """
    Returns a list of days in the given month with available hours and max hours for the user.
    Query params: year, month (1-based)
    """
    profile = request.user.profile
    
    try:
        year = int(request.query_params.get('year', date.today().year))
        month = int(request.query_params.get('month', date.today().month))
    except (ValueError, TypeError):
        return Response(
            {"error": "Invalid year or month parameter. Must be integers."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate month range
    if month < 1 or month > 12:
        return Response(
            {"error": "Month must be between 1 and 12."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate year range (reasonable bounds)
    if year < 1900 or year > 2100:
        return Response(
            {"error": "Year must be between 1900 and 2100."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    days_in_month = monthrange(year, month)[1]
    start = date(year, month, 1)
    end = date(year, month, days_in_month)

    # Check if we have recent Google Calendar data for this month
    google_entries_count = CalendarEntry.objects.filter(
        user=profile,
        start_date__gte=start,
        start_date__lte=end,
        source='google'
    ).count()
    
    # If no Google Calendar data exists for this month, trigger sync
    if google_entries_count == 0:
        token = get_google_token(profile.user.id)
        if token:
            # Convert dates to datetime for the sync task with proper timezone
            from datetime import datetime, time, timezone
            start_dt = datetime.combine(start, time.min).replace(tzinfo=timezone.utc)
            end_dt = datetime.combine(end, time.max).replace(tzinfo=timezone.utc)
            
            sync_google_calendar_task.delay(
                user_id=profile.user.id,
                start_iso=start_dt.isoformat(),
                end_iso=end_dt.isoformat(),
                calendar_ids=["primary"]
            )

    # Get all timeslots for this user in the month
    timeslots = TimeSlot.objects.filter(
        user=profile,
        start_date__gte=start,
        start_date__lte=end
    )
    
    # Get Google Calendar busy slots (these reduce availability)
    google_busy_slots = CalendarEntry.objects.filter(
        user=profile,
        start_date__gte=start,
        start_date__lte=end,
        source='google'
    )

    # Aggregate available hours per day from manual timeslots
    daily_available = {}
    for ts in timeslots:
        d = ts.start_date.isoformat()
        daily_available.setdefault(d, 0)
        daily_available[d] += ts.duration / 60  # duration is in minutes

    # Aggregate busy hours per day from Google Calendar
    daily_busy = {}
    for entry in google_busy_slots:
        d = entry.start_date.isoformat()
        daily_busy.setdefault(d, 0)
        daily_busy[d] += entry.duration / 60  # duration is in minutes

    # Assume max available hours per day is 8 (customize as needed)
    max_hours = 8
    result = []
    for day in range(1, days_in_month + 1):
        d = date(year, month, day).isoformat()
        available = daily_available.get(d, 0)
        busy = daily_busy.get(d, 0)
        
        # If we have manual availability, subtract busy time
        # If no manual availability is set, assume full day is available minus busy time
        if available > 0:
            net_available = max(0, available - busy)
        else:
            # Default availability minus busy time
            net_available = max(0, max_hours - busy)
        
        result.append({
            'date': d,
            'availableHours': round(net_available, 2),
            'maxHours': max_hours
        })
    
    return Response(result)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def submit_availability(request):
    """
    Submit participant availability for an event within the host's specified time range
    
    Expected payload:
    {
        "event_id": <event_id>,
        "availability_slots": [
            {
                "start_datetime": "2025-07-30T09:00:00Z",
                "end_datetime": "2025-07-30T10:00:00Z",
                "availability": "available"
            }
        ]
    }
    """
    from .models import ParticipantAvailability
    from .serializers import ParticipantAvailabilitySerializer
    
    try:
        event_id = request.data.get('event_id')
        availability_slots = request.data.get('availability_slots', [])
        
        event = Event.objects.get(id=event_id)
        participant = request.user.profile
        
        # Check if user is a participant
        if not event.participants.filter(id=participant.id).exists():
            return Response(
                {"error": "You are not a participant of this event."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if event is in availability collection phase
        if event.status != 'collecting_availability':
            return Response(
                {"error": "Event is not currently collecting availability."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Clear existing availability for this participant and event
        ParticipantAvailability.objects.filter(
            participant=participant,
            event=event
        ).delete()
        
        # Create new availability entries
        for slot in availability_slots:
            ParticipantAvailability.objects.create(
                participant=participant,
                event=event,
                start_datetime=slot['start_datetime'],
                end_datetime=slot['end_datetime'],
                availability=slot.get('availability', 'available')
            )
        
        return Response({
            "message": "Availability submitted successfully",
            "slots_submitted": len(availability_slots)
        }, status=status.HTTP_201_CREATED)
        
    except Event.DoesNotExist:
        return Response(
            {"error": "Event not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_availability_for_event(request, event_id):
    """
    Get availability submitted by the current user for a specific event
    """
    from .models import ParticipantAvailability
    from .serializers import ParticipantAvailabilitySerializer
    
    try:
        event = Event.objects.get(id=event_id)
        participant = request.user.profile
        
        # Check if user is a participant
        if not event.participants.filter(id=participant.id).exists():
            return Response(
                {"error": "You are not a participant of this event."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        availabilities = ParticipantAvailability.objects.filter(
            participant=participant,
            event=event
        ).order_by('start_datetime')
        
        serializer = ParticipantAvailabilitySerializer(availabilities, many=True)
        
        return Response({
            "event_id": event_id,
            "participant": participant.user.username,
            "availability_slots": serializer.data
        }, status=status.HTTP_200_OK)
        
    except Event.DoesNotExist:
        return Response(
            {"error": "Event not found."},
            status=status.HTTP_404_NOT_FOUND
        )
