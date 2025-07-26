from rest_framework import serializers
from accounts.models import Profile
from dj_rest_auth.registration.serializers import SocialLoginSerializer
from allauth.socialaccount.models import SocialAccount, SocialToken, SocialApp
from django.conf import settings
import os

"""
accounts/serializers.py

Contains serializers to validate and parse incoming request data for the accounts app.
"""


class GoogleLoginSerializer(SocialLoginSerializer):
    """
    Custom Google login serializer for context management.
    Token storage is handled in the view after successful authentication.
    """
    
    def validate(self, attrs):
        # Ensure we have proper context
        request = self.context.get('request')
        
        if not request:
            raise serializers.ValidationError("Request context is required")
        
        # Call parent validation
        validated_attrs = super().validate(attrs)
        
        return validated_attrs


class ProfileSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    def get_name(self, obj):
        user = obj.user
        return f"{user.first_name} {user.last_name}".strip()

    def get_user(self, obj):
        return obj.user.username

    class Meta:
        model = Profile
        fields = ["name", "user"]


class FreeBusyRequestSerializer(serializers.Serializer):
    """
    Serializer for validating start and end datetime fields for Google Calendar FreeBusy API requests.
    It now also accepts an optional list of calendar IDs.
    """

    start = serializers.DateTimeField()  # Start datetime (ISO 8601)
    end = serializers.DateTimeField()  # End datetime (ISO 8601)
    calendars = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=["primary"],  # Defaults to the primary calendar if not specified
    )
