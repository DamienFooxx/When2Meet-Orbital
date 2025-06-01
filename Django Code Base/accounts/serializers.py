from rest_framework import serializers

"""
accounts/serializers.py

Contains serializers to validate and parse incoming request data for the accounts app.
"""

class FreeBusyRequestSerializer(serializers.Serializer):
    """
    Serializer for validating start and end datetime fields for Google Calendar FreeBusy API requests.
    """
    start = serializers.DateTimeField()  # Start datetime (ISO 8601)
    end = serializers.DateTimeField()    # End datetime (ISO 8601)