from django.shortcuts import render
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .serializers import FreeBusyRequestSerializer
import requests
from allauth.socialaccount.models import SocialAccount, SocialToken
from rest_framework.response import Response

"""
accounts/views.py

Contains custom authentication views, including Google OAuth login.
"""

# Create your views here.
class GoogleCalendarFreeBusyView(APIView):
    """
    API endpoint to fetch a user's busy slots from their Google Calendar using the FreeBusy API.
    Requires the user to be authenticated and have a connected Google account.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Handles POST requests to fetch busy slots between 'start' and 'end' datetimes.
        Expects 'start' and 'end' in the request body (ISO 8601 format).
        Returns a list of busy time slots from the user's primary Google Calendar.
        """
        serializer = FreeBusyRequestSerializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        start = serializer.validated_data['start']
        end = serializer.validated_data['end']

        # Get user's Google access token
        try:
            social_account = SocialAccount.objects.get(user = request.user, provider = 'google')
            social_token = SocialToken.objects.get(account = social_account)
        except (SocialAccount.DoesNotExist, SocialToken.DoesNotExist):
            return Response({"error" : "Google account not connected"}, status = 400)

        access_token = social_token.token

        # Call Google Calendar FreeBusy API
        url = "https://www.googleapis.com/calendar/v3/freeBusy"
        headers = {"Authorization" : f"Bearer {access_token}"}
        data = {
            "timeMin": start.isoformat() + "Z",
            "timeMax": end.isoformat() + "Z",
            "items": [{"id": "primary"}]
        }
        resp = requests.post(url, headers = headers, json = data)
        if resp.status_code == 401:  # Unauthorized - likely expired/invalid token
            return Response({
                "error": "Google token expired or invalid. Please reconnect your Google account."
            }, status=401)
        elif resp.status_code != 200:
            return Response({
                "error": "Failed to fetch from Google Calendar",
                "details" : resp.json()
                }, status = resp.status_code)

        freebusy = resp.json()
        # Returns the busy slots from "primary" calendar
        busy_slots = freebusy.get("calendars", {}).get("primary", {}).get("busy", [])
        return Response({"busy": busy_slots})