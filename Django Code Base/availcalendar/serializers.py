from rest_framework import serializers
from availcalendar.models import (
    TimeSlot,
    ManualAvailability,
    CalendarIntegration,
    CalendarEntry,
    Reminder,
)
from events.models import Event
from accounts.models import Profile, Location
from datetime import datetime


class TimeSlotSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=Profile.objects.all())
    event = serializers.PrimaryKeyRelatedField(
        queryset=Event.objects.all(), allow_null=True, required=False, source="event_id"
    )

    class Meta:
        model = TimeSlot
        fields = [
            "id",
            "event",
            "user",
            "start_date",
            "start_time",
            "end_date",
            "end_time",
            "duration",
            "status",
        ]
        read_only_fields = ["id"]

    def validate(self, data):
        start = datetime.combine(data["start_date"], data["start_time"])
        end = datetime.combine(data["end_date"], data["end_time"])
        if end <= start:
            raise serializers.ValidationError({"end_date": "End must be after start."})
        expected_duration = int((end - start).total_seconds() // 60)
        if data["duration"] != expected_duration:
            raise serializers.ValidationError(
                {"duration": "Duration does not match start/end."}
            )
        if expected_duration % 15 != 0:
            raise serializers.ValidationError(
                {"duration": "Duration must be a multiple of 15 minutes."}
            )
        for t, name in (
            (data["start_time"], "start_time"),
            (data["end_time"], "end_time"),
        ):
            if t.minute % 15 != 0 or t.second != 0 or t.microsecond != 0:
                raise serializers.ValidationError(
                    {
                        name: f"{name} must be on a 15-minute boundary (e.g. 00, 15, 30, 45)."
                    }
                )
        return data


class CalendarEntrySerializer(serializers.ModelSerializer):
    location = serializers.PrimaryKeyRelatedField(
        source="location_id",
        queryset=Location.objects.all(),
        allow_null=True,
        required=False,
    )
    user = serializers.PrimaryKeyRelatedField(
        source="user_id", queryset=Profile.objects.all()
    )
    event = serializers.PrimaryKeyRelatedField(
        source="event_id", queryset=Event.objects.all()
    )

    class Meta:
        model = CalendarEntry
        fields = [
            "id",
            "title",
            "description",
            "start_date",
            "start_time",
            "end_date",
            "end_time",
            "duration",
            "created_at",
            "updated_at",
            "source",
            "google_event_id",
            "location",
            "user",
            "event",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, data):
        start = datetime.combine(data["start_date"], data["start_time"])
        end = datetime.combine(data["end_date"], data["end_time"])
        if end <= start:
            raise serializers.ValidationError({"end_date": "End must be after start."})
        expected_duration = int((end - start).total_seconds() // 60)
        if data["duration"] != expected_duration:
            raise serializers.ValidationError(
                {"duration": "Duration does not match start/end."}
            )
        if expected_duration % 15 != 0:
            raise serializers.ValidationError(
                {"duration": "Duration must be a multiple of 15 minutes."}
            )
        for t, name in (
            (data["start_time"], "start_time"),
            (data["end_time"], "end_time"),
        ):
            if t.minute % 15 != 0 or t.second != 0 or t.microsecond != 0:
                raise serializers.ValidationError(
                    {
                        name: f"{name} must be on a 15-minute boundary (e.g. 00, 15, 30, 45)."
                    }
                )
        return data


class CalendarIntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalendarIntegration
        fields = [
            "id",
            "provider",
            "external_id",
            "access_token",
            "refresh_token",
            "token_expiry",
            "user",
        ]
        read_only_fields = ["id", "provider"]


class ManualAvailabilitySerializer(serializers.ModelSerializer):
    # Write only field to dictate how often the event should recur
    freq = serializers.ChoiceField(
        choices=[
            ("DAILY", "Daily"),
            ("WEEKLY", "Weekly"),
            ("MONTHLY", "Monthly"),
            ("YEARLY", "Yearly"),
        ],
        write_only=True,
    )
    # Write only field to dictate the interval between the frequencies
    interval = serializers.IntegerField(default=1, write_only=True)
    by_day = serializers.ListField(
        child=serializers.ChoiceField(
            choices=["MO", "TU", "WE", "TH", "FR", "SA", "SU"]
        ),
        required=False,
        write_only=True,
    )
    until = serializers.DateTimeField(required=False, write_only=True)
    count = serializers.IntegerField(required=False, write_only=True)

    class Meta:
        model = ManualAvailability
        fields = [
            "id",
            "start_date",
            "start_time",
            "end_date",
            "end_time",
            "duration",
            "freq",
            "interval",
            "by_day",
            "until",
            "count",
            "recurrence",
        ]
        read_only_fields = ["id", "recurrence"]

    def _build_rrule(self, validated_data):
        parts = [
            f"FREQ = {validated_data['freq']}",
            f"INTERVAL = {validated_data['interval']}",
        ]
        if "by_day" in validated_data and validated_data["by_day"]:
            parts.append("BYDAY =" + ",".join(validated_data["by_day"]))
        if "until" in validated_data and validated_data["until"]:
            # RFC-5545 wants UTC 'YYYYMMDDTHHMMSSZ'
            dt = validated_data["until"].strftime("%Y%m%dT%H%M%SZ")
            parts.append(f"UNTIL = {dt}")
        if "count" in validated_data and validated_data["count"]:
            parts.append(f"COUNT ={validated_data['count']}")
        return ";".join(parts)

    def create(self, validated_data):
        # Extract and remove RRULE parts from the payload
        rrule_data = {
            k: validated_data.pop(k)
            for k in ["freq", "interval", "by_day", "until", "count"]
            if k in validated_data
        }
        # Build and inject the recurrence string
        validated_data["recurrence"] = self._build_rrule(rrule_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Same RRULE logic on updates
        rrule_data = {
            k: validated_data.pop(k)
            for k in ["freq", "interval", "by_day", "until", "count"]
            if k in validated_data
        }
        if rrule_data:
            validated_data["recurrence"] = self._build_rrule(rrule_data)
        return super().update(instance, validated_data)

    def validate(self, data):
        start = datetime.combine(data["start_date"], data["start_time"])
        end = datetime.combine(data["end_date"], data["end_time"])
        if end <= start:
            raise serializers.ValidationError({"end_date": "End must be after start."})
        expected_duration = int((end - start).total_seconds() // 60)
        if data["duration"] != expected_duration:
            raise serializers.ValidationError(
                {"duration": "Duration does not match start/end."}
            )
        if expected_duration % 15 != 0:
            raise serializers.ValidationError(
                {"duration": "Duration must be a multiple of 15 minutes."}
            )
        for t, name in (
            (data["start_time"], "start_time"),
            (data["end_time"], "end_time"),
        ):
            if t.minute % 15 != 0 or t.second != 0 or t.microsecond != 0:
                raise serializers.ValidationError(
                    {
                        name: f"{name} must be on a 15-minute boundary (e.g. 00, 15, 30, 45)."
                    }
                )
        return data


class ReminderSerializer(serializers.ModelSerializer):
    # Expose the FK fields under nicer names
    calendar_entry = serializers.PrimaryKeyRelatedField(
        source="calendar_entry_id", queryset=CalendarEntry.objects.all()
    )
    user = serializers.PrimaryKeyRelatedField(
        source="user_id", queryset=Profile.objects.all()
    )

    class Meta:
        model = Reminder
        fields = [
            "id",
            "remind_at",
            "calendar_entry",
            "user",
        ]
        read_only_fields = ["id"]
