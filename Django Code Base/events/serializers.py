from rest_framework import serializers
from .models import Event, EventParticipant
from accounts.models import Profile, Location


class EventParticipantSerializer(serializers.ModelSerializer):
    """
    Serializer for the EventParticipant model to show participant details.
    """

    participant_id = serializers.ReadOnlyField(source="participant.pk")
    participant_name = serializers.ReadOnlyField(source="participant.name")

    class Meta:
        model = EventParticipant
        fields = ["participant_id", "participant_name", "is_joining"]


class EventSerializer(serializers.ModelSerializer):
    location = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(),
        allow_null=True,
        source="location_id",
        required=False,
    )
    creator = serializers.PrimaryKeyRelatedField(queryset=Profile.objects.all())
    participants = EventParticipantSerializer(
        source="eventparticipant_set", many=True, read_only=True
    )
    participants_to_add = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Profile.objects.all(), write_only=True, required=False
    )

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "description",
            "created_at",
            "creator",
            "location",
            "group",
            "participants",
            "participants_to_add",
        ]
        read_only_fields = ["id", "created_at"]

    def create(self, validated_data):
        # Pop the participants data from the validated data
        participants_data = validated_data.pop("participants_to_add", [])

        # Create event instance
        event = Event.objects.create(**validated_data)

        # The creator should always be a participant
        EventParticipant.objects.create(
            event=event, participant=event.creator, is_joining="going"
        )

        # Create EventParticipant entries for the other participants
        for profile in participants_data:
            # Avoid creating a duplicate for the creator
            if profile != event.creator:
                EventParticipant.objects.create(
                    event=event, participant=profile, is_joining="maybe"
                )  # Default to 'maybe'

        return event
