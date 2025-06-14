from rest_framework import serializers
from accounts.models import Profile

"""
accounts/serializers.py

Contains serializers to validate and parse incoming request data for the accounts app.
"""

class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for Profile model.
    """
    username = serializers.CharField(source='user.username')
    name = serializers.CharField(source='name')

    class Meta:
        model = Profile
        fields = ['id', 'username', 'name']

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