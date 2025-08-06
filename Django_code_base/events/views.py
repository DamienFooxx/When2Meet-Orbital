from django.db.models import Q
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from events.models import Event, EventParticipant
from events.serializers import EventSerializer, EventParticipantSerializer
from groups.models import GroupMembership

# Create your views here.


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

    def destroy(self, request, *args, **kwargs):
        event = self.get_object()
        user_profile = request.user.profile
        # If event is linked to a group, check organiser role
        if event.group:
            is_organiser = GroupMembership.objects.filter(
                group=event.group,
                profile=user_profile,
                role="organiser",
                is_accepted=True,
            ).exists()
            if not is_organiser:
                return Response(
                    {"detail": "Only organisers can delete events from the group."},
                    status=status.HTTP_403_FORBIDDEN,
                )
        else:
            # If not a group event, only creator can delete
            if event.creator != user_profile:
                return Response(
                    {"detail": "Only the creator can delete this event."},
                    status=status.HTTP_403_FORBIDDEN,
                )
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'], url_path='start-availability-collection')
    def start_availability_collection(self, request, pk=None):
        """
        Start the availability collection phase for an event
        """
        event = self.get_object()
        
        # Check if user is the creator
        if event.creator != request.user.profile:
            return Response(
                {"error": "Only the event creator can start availability collection."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Update event status
        event.status = 'collecting_availability'
        event.save()
        
        return Response({
            "message": "Availability collection started",
            "event_id": event.id,
            "status": event.status
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='check-and-create-poll')
    def check_and_create_poll(self, request, pk=None):
        """
        Check if all participants have submitted availability and create poll if multiple slots available
        """
        from availcalendar.models import ParticipantAvailability
        from smartScheduling.scheduling_engine import schedule_best_timeslots
        from polls.models import Poll, PollOption
        from availcalendar.models import TimeSlot
        
        event = self.get_object()
        
        # Check if user is the creator
        if event.creator != request.user.profile:
            return Response(
                {"error": "Only the event creator can manage polls."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if event is in availability collection phase
        if event.status != 'collecting_availability':
            return Response(
                {"error": "Event is not in availability collection phase."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get all participants
        participants = event.participants.all()
        participants_with_availability = ParticipantAvailability.objects.filter(
            event=event
        ).values_list('participant', flat=True).distinct()
        
        # Check if all participants have submitted availability
        missing_participants = participants.exclude(
            id__in=participants_with_availability
        )
        
        if missing_participants.exists():
            missing_names = [p.user.username for p in missing_participants]
            return Response({
                "message": "Not all participants have submitted availability",
                "missing_participants": missing_names,
                "total_participants": participants.count(),
                "submitted": len(participants_with_availability)
            }, status=status.HTTP_200_OK)
        
        # All participants have submitted - run smart scheduling
        try:
            # Convert availability data for smart scheduling
            # This is a simplified version - you may need to adapt based on your scheduling engine
            slots = schedule_best_timeslots(
                users=list(participants),
                start_date=event.availability_start_date,
                start_time=event.availability_start_time,
                end_date=event.availability_end_date,
                end_time=event.availability_end_time,
                duration=event.duration_minutes or 60,
                buffer=15,
                min_attendance=0.5
            )
            
            if not slots:
                event.status = 'confirmed'
                event.save()
                return Response({
                    "message": "No suitable time slots found. Event needs manual scheduling.",
                    "status": "no_slots_found"
                }, status=status.HTTP_200_OK)
            
            # If only one slot, confirm it directly
            if len(slots) == 1:
                # Get the single slot details
                slot_info = list(slots.items())[0]
                start_datetime, end_datetime = slot_info[0]
                
                # Create TimeSlot and confirm event
                timeslot = TimeSlot.objects.create(
                    event_id=event,
                    start_date=start_datetime.date(),
                    start_time=start_datetime.time(),
                    end_date=end_datetime.date(),
                    end_time=end_datetime.time(),
                    duration=event.duration_minutes or 60,
                    status='confirmed'
                )
                
                event.confirmed_timeslot = timeslot
                event.status = 'confirmed'
                event.save()
                
                return Response({
                    "message": "Single time slot found and confirmed",
                    "status": "confirmed",
                    "timeslot": {
                        "start": start_datetime,
                        "end": end_datetime
                    }
                }, status=status.HTTP_200_OK)
            
            # Multiple slots - create poll
            poll = Poll.objects.create(event=event)
            
            for (start_datetime, end_datetime), slot_info in slots.items():
                timeslot = TimeSlot.objects.create(
                    event_id=event,
                    start_date=start_datetime.date(),
                    start_time=start_datetime.time(),
                    end_date=end_datetime.date(),
                    end_time=end_datetime.time(),
                    duration=event.duration_minutes or 60,
                    status='not confirmed'
                )
                
                PollOption.objects.create(
                    poll=poll,
                    timeslot=timeslot
                )
            
            event.status = 'polling'
            event.save()
            
            return Response({
                "message": "Multiple suitable slots found. Poll created.",
                "status": "polling",
                "poll_id": poll.id,
                "options_count": len(slots)
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {"error": f"Smart scheduling failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class EventParticipantViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only viewset to list participants and their status for a given event.
    Filter by ?event=<event_id>
    """
    serializer_class = EventParticipantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = EventParticipant.objects.all()
        event_id = self.request.query_params.get('event')
        if event_id:
            queryset = queryset.filter(event__id=event_id)
        return queryset
