from rest_framework import serializers
from accounts.models import Profile

"""
accounts/serializers.py

Contains serializers to validate and parse incoming request data for the accounts app.
"""

class ProfileSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        user = obj.user
        return f"{user.first_name} {user.last_name}".strip()

    class Meta:
        model = Profile
        fields = ['name']

class FreeBusyRequestSerializer(serializers.Serializer):
    """
    Serializer for validating start and end datetime fields for Google Calendar FreeBusy API requests.
    It now also accepts an optional list of calendar IDs.
    """
    start = serializers.DateTimeField()  # Start datetime (ISO 8601)
    end = serializers.DateTimeField()    # End datetime (ISO 8601)
    calendars = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=['primary'] # Defaults to the primary calendar if not specified
    )