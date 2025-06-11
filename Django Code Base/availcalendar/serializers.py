from rest_framework import serializers
from .models import Event, TimeSlot, ManualAvailability, CalendarIntegration, CalendarEntry, Reminder
from accounts.models import Profile, Location
from datetime import datetime

class EventSerializer(serializers.ModelSerializer):
    location = serializers.PrimaryKeyRelatedField(queryset = Location.objects.all(), allow_null=True)
    creator = serializers.PrimaryKeyRelatedField(queryset = Profile.objects.all())
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
    user  = serializers.PrimaryKeyRelatedField(queryset = Profile.objects.all())
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

class ManualAvailabilitySerializer(serializers.ModelSerializer):
    freq = serializers.ChoiceField(
        choices=[
            ('DAILY','Daily'),
            ('WEEKLY','Weekly'),
            ('MONTHLY','Monthly'),
            ('YEARLY','Yearly')
            ],
        write_only=True
    )
    interval = serializers.IntegerField(default=1, write_only=True)
    by_day = serializers.ListField(
        child=serializers.ChoiceField(choices=['MO','TU','WE','TH','FR','SA','SU']),
        required=False,
        write_only=True
        )
    until = serializers.DateTimeField(required=False, write_only=True)
    count = serializers.IntegerField(required=False, write_only=True)

    class Meta:
        model = ManualAvailability
        fields = ['start_time','end_time','freq','interval','by_day','until','count','recurrence']
        read_only_fields = ['recurrence']

    def _build_rrule(self, validated_data):
        parts = [
            f"FREQ = {validated_data['freq']}",
            f"INTERVAL = {validated_data['interval']}"
        ]
        if 'by_day' in validated_data and validated_data['by_day']:
            parts.append("BYDAY =" + ",".join(validated_data['by_day']))
        if 'until' in validated_data and validated_data['until']:
            # RFC-5545 wants UTC 'YYYYMMDDTHHMMSSZ'
            dt = validated_data['until'].strftime("%Y%m%dT%H%M%SZ")
            parts.append(f"UNTIL = {dt}")
        if 'count' in validated_data and validated_data['count']:
            parts.append(f"COUNT ={validated_data['count']}")
        return ";".join(parts)

    def create(self, validated_data):
        # Extract and remove RRULE parts from the payload
        rrule_data = {k: validated_data.pop(k) 
                      for k in ['freq','interval','by_day','until','count']
                      if k in validated_data}
        # Build and inject the recurrence string
        validated_data['recurrence'] = self._build_rrule(rrule_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Same RRULE logic on updates
        rrule_data = {k: validated_data.pop(k) 
                      for k in ['freq','interval','by_day','until','count']
                      if k in validated_data}
        if rrule_data:
            validated_data['recurrence'] = self._build_rrule(rrule_data)
        return super().update(instance, validated_data)

class CalendarIntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalendarIntegration
        fields = [
            'id',
            'provider',
            'external_id',
            'access_token',
            'refresh_token',
            'token_expiry',
        ]
        read_only_fields = ['id', 'provider', 'external_id']

class CalendarEntrySerializer(serializers.ModelSerializer):
    # Expose nicer field names and map them to the FK attributes
    location = serializers.PrimaryKeyRelatedField(
        source='location_id',
        queryset=Location.objects.all(),
        allow_null=True,
        required=False
    )
    user = serializers.PrimaryKeyRelatedField(
        source='user_id',
        queryset=Profile.objects.all()
    )
    event = serializers.PrimaryKeyRelatedField(
        source='event_id',
        queryset=Event.objects.all()
    )

    class Meta:
        model = CalendarEntry
        fields = [
            'id',
            'title',
            'description',
            'start_time',
            'end_time',
            'created_at',
            'updated_at',
            'source',
            'google_event_id',
            'location',
            'user',
            'event',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class ReminderSerializer(serializers.ModelSerializer):
    # Expose the FK fields under nicer names
    calendar_entry = serializers.PrimaryKeyRelatedField(
        source='calendar_entry_id',
        queryset=CalendarEntry.objects.all()
    )
    user = serializers.PrimaryKeyRelatedField(
        source='user_id',
        queryset=Profile.objects.all()
    )

    class Meta:
        model = Reminder
        fields = [
            'id',
            'remind_at',
            'calendar_entry',
            'user',
        ]
        read_only_fields = ['id']