from django.db import transaction
from rest_framework import serializers
from polls.models import Poll, PollOption, PollVote
from events.models import Event
from availcalendar.models import TimeSlot
from accounts.serializers import ProfileSerializer
from accounts.models import Profile


class PollOptionSerializer(serializers.ModelSerializer):
    """
    Handles a single candidate timeslot inside a poll.
    """
    start_date = serializers.ReadOnlyField(source="timeslot.start_date")
    start_time = serializers.ReadOnlyField(source="timeslot.start_time")
    end_date = serializers.ReadOnlyField(source="timeslot.end_date")
    end_time = serializers.ReadOnlyField(source="timeslot.end_time")
    vote_count = serializers.SerializerMethodField()

    class Meta:
        model  = PollOption
        fields = ["id", "timeslot", "start_date", "start_time",
                  "end_date", "end_time", "vote_count"]

    def get_vote_count(self, obj):
        return obj.votes.count()


class PollVoteSerializer(serializers.ModelSerializer):
    """
    Records a single person’s vote for a PollOption.
    """
    voter = ProfileSerializer(read_only=True)

    class Meta:
        model  = PollVote
        fields = ["id", "poll_option", "voter", "voted_at"]
        read_only_fields = ["id", "voter", "voted_at"]

    def validate(self, attrs):
        request = self.context["request"]
        voter_prof = Profile.objects.get(user=request.user)
        option = attrs["poll_option"]

        if PollVote.objects.filter(poll_option=option, voter=voter_prof).exists():
            raise serializers.ValidationError("You have already voted for this option.")
        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        voter_prof = Profile.objects.get(user=request.user)
        return PollVote.objects.create(voter=voter_prof, **validated_data)


class PollSerializer(serializers.ModelSerializer):
    """
    Top-level poll for an Event.
    Accepts a list of timeslot IDs when creating; returns full option details when retrieving.
    """
    event = serializers.PrimaryKeyRelatedField(queryset=Event.objects.all())
    options = PollOptionSerializer(many=True, read_only=True)
    option_ids = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(
            queryset=TimeSlot.objects.all()
        ),
        write_only=True,
        required=True,
        help_text="List of TimeSlot IDs to include as poll options when creating."
    )
    total_votes = serializers.SerializerMethodField()

    class Meta:
        model  = Poll
        fields = ["id", "created_at", "event", "option_ids", "options", "total_votes"]
        read_only_fields = ["id", "created_at", "options", "total_votes"]

    def get_total_votes(self, obj):
        return PollVote.objects.filter(poll_option__poll=obj).count()

    def create(self, validated_data):
        """
        Atomically create the Poll and its PollOption rows.
        """
        option_timeslots = validated_data.pop("option_ids")

        with transaction.atomic():
            poll = Poll.objects.create(**validated_data)

            for ts in option_timeslots:
                if ts.event != poll.event:
                    raise serializers.ValidationError(
                        f"Timeslot {ts.id} does not belong to Event {poll.event.id}"
                    )
                PollOption.objects.create(poll=poll, timeslot=ts)

        return poll

class PollGenerateSerializer(serializers.Serializer):
    """
    Input parameters for the smart scheduling engine.
    Used only by the custom /generate/ endpoint.
    """
    event = serializers.PrimaryKeyRelatedField(queryset=Event.objects.all())
    start_date = serializers.DateField()
    start_time = serializers.TimeField()
    end_date = serializers.DateField()
    end_time = serializers.TimeField()
    duration = serializers.IntegerField(min_value=15)
    buffer = serializers.IntegerField(min_value=0)
    min_attendance = serializers.FloatField(min_value=0.0, max_value=1.0)

    def validate_event(self, event):
        if not event.participants.exists():
            raise serializers.ValidationError("Event has no participants.")
        return event

