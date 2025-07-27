from django.db import models, transaction
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from accounts.models import Profile
from events.models import Event
from availcalendar.models import TimeSlot
from smartScheduling.scheduling_engine import schedule_best_timeslots
from polls.models import Poll, PollOption, PollVote
from polls.serializers import (
    PollSerializer,
    PollGenerateSerializer,
    PollOptionSerializer,
    PollVoteSerializer,
)

def _is_event_organiser(profile: Profile, event: Event) -> bool:
    """
    A simple organiser check.
    """
    return event.creator == profile

class PollViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing, creating, generating, and deleting polls.
    Only authenticated users may access these endpoints.
    """

    queryset = Poll.objects.all().select_related("event")
    serializer_class = PollSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """
        Manual creation via POST /polls/  (payload uses `option_ids` list)
        Enforce: only event organisers may create a poll.
        """
        profile = Profile.objects.get(user=self.request.user)
        event: Event = serializer.validated_data["event"]

        if not _is_event_organiser(profile, event):
            raise permissions.PermissionDenied(
                "Only event organisers can create a poll."
            )
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        poll = self.get_object()
        profile = Profile.objects.get(user=request.user)
        if not _is_event_organiser(profile, poll.event):
            return Response(
                {"error": "Only organisers can delete the poll."},
                status=status.HTTP_403_FORBIDDEN,
            )
        poll.delete()
        return Response(
            {"message": "Poll deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )

    @action(detail=False, methods=["post"], url_path="generate")
    def generate_poll(self, request):
        """
        POST /polls/generate/

        Runs smart-scheduler, creates a poll with the
        returned top time-slots, and sends back the full poll payload.

        Expected JSON body:
        {
          "event":          <event_id>,
          "start_date":     "YYYY-MM-DD",
          "start_time":     "HH:MM",
          "end_date":       "YYYY-MM-DD",
          "end_time":       "HH:MM",
          "duration":       <minutes>,
          "buffer":         <minutes>,
          "min_attendance": 0.5
        }
        """
        serializer = PollGenerateSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        event = data["event"]
        profile = Profile.objects.get(user=request.user)

        if not _is_event_organiser(profile, event):
            return Response(
                {"error": "Only organisers can generate a poll."},
                status=status.HTTP_403_FORBIDDEN,
            )

        participants = list(
            event.participants.select_related("profile").values_list(
                "profile", flat=True
            )
        )
        users = Profile.objects.filter(id__in=participants)

        suggested = schedule_best_timeslots(
            users = users,
            start_date = data["start_date"],
            start_time = data["start_time"],
            end_date = data["end_date"],
            end_time = data["end_time"],
            duration = data["duration"],
            buffer = data["buffer"],
            min_attendance = data["min_attendance"],
        )

        if not suggested:
            return Response(
                {
                    "error": "No timeslots fit the criteria. "
                             "Adjust the date range or attendance threshold."
                },
                status=status.HTTP_204_NO_CONTENT,
            )

    with transaction.atomic():
        poll = Poll.objects.create(event=event)

        option_objs = []
        for slot in suggested:
            start_d = slot['start_date']
            start_t = slot['start_time']
            end_d   = slot['end_date']
            end_t   = slot['end_time']
            dur     = slot['duration']

            ts, _ = TimeSlot.objects.get_or_create(
                event=event_id,
                start_date=start_d,
                start_time=start_t,
                end_date=end_d,
                end_time=end_t,
                defaults={
                    'duration': dur,
                    'status':   'not confirmed',
                    'user':     None,
                    'created_at': timezone.now(),
                },
            )
            option_objs.append(PollOption(poll=poll, timeslot=ts))

        PollOption.objects.bulk_create(option_objs)

        return Response(
            PollSerializer(poll, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["get"], url_path="options")
    def list_options(self, request, pk=None):
        """
        Lists all poll options (with vote counts) for a given poll.
        """
        poll = self.get_object()
        options = poll.options.select_related("timeslot").all()
        serializer = PollOptionSerializer(options, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class PollOptionViewSet(viewsets.ModelViewSet):
    """
    List or remove individual poll options.
    Organisers may prune options after generation.
    """

    queryset = PollOption.objects.all().select_related("poll", "timeslot")
    serializer_class = PollOptionSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "delete"]

    def destroy(self, request, *args, **kwargs):
        option = self.get_object()
        profile = Profile.objects.get(user=request.user)

        if not _is_event_organiser(profile, option.poll.event):
            return Response(
                {"error": "Only organisers can delete poll options."},
                status=status.HTTP_403_FORBIDDEN,
            )
        option.delete()
        return Response(
            {"message": "Poll option removed."},
            status=status.HTTP_204_NO_CONTENT,
        )

class PollVoteViewSet(viewsets.ModelViewSet):
    """
    Cast or revoke votes.
    One vote per user **per option** (enforced by model unique_together).
    """

    queryset = PollVote.objects.all().select_related("poll_option", "voter")
    serializer_class = PollVoteSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["post", "delete"]

    def perform_create(self, serializer):
        """
        POST /poll-votes/
        Payload: { "poll_option": <option_id> }
        """
        voter = Profile.objects.get(user=self.request.user)
        option = serializer.validated_data["poll_option"]

        event = option.poll.event
        if not event.participants.filter(profile=voter).exists():
            raise permissions.PermissionDenied("You are not a participant of this event.")

        serializer.save(voter=voter)

    def destroy(self, request, *args, **kwargs):
        vote = self.get_object()
        if vote.voter.user != request.user:
            return Response(
                {"error": "You can only revoke your own vote."},
                status=status.HTTP_403_FORBIDDEN,
            )
        vote.delete()
        return Response(
            {"message": "Vote removed."},
            status=status.HTTP_204_NO_CONTENT,
        )
