from rest_framework import serializers
from geopy.geocoders import GoogleV3
from models import Profile
import os


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

class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for validating and parsing address data.
    """
    geolocator = GoogleV3(api_key=os.getenv('GOOGLE_MAPS_API_KEY'))

    class Meta:
        model = Profile
        fields = '__all__'

    def validate(self, data):
        address = f"{data.get('street_address', '')}, {data.get('state', '')}, {data.get('country', '')}"
        geolocator = GoogleV3(api_key=os.getenv('GOOGLE_MAPS_API_KEY'))
        location = geolocator.geocode(address)
        if not location:
            raise serializers.ValidationError("Invalid address. Please check your entry.")
        return data
