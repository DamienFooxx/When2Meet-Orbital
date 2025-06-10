from rest_framework import serializers
from .models import Event, TimeSlot
from accounts.models import Profile, Location

class EventSerializer(serializers.ModelSerializer):
    location = serializers.PrimaryKeyRelatedField(queryset = accounts.Location.objects.all(), allow_null=True)
    creator = serializers.PrimaryKeyRelatedField(queryset = accounts.Profile.objects.all())
    participants = serializers.PrimaryKeyRelatedField(
        many = True,
        queryset = Profile.objects.all()
    )

    class Meta:
        model = Event
        fields = [
            'id',
            'title',
            'description',
            'location',
            'creator',
            'participants',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class TimeSlotSerializer(serializers.ModelSerializer):
    user  = serializers.PrimaryKeyRelatedField(queryset = accounts.Profile.objects.all())
    event = serializers.PrimaryKeyRelatedField(queryset= Event.objects.all(), allow_null = True, required = False)

    class Meta:
        model = TimeSlot
        fields = [
            'id',
            'user',
            'event',
            'start',
            'end',
            'source',
        ]
        read_only_fields = ['id']
