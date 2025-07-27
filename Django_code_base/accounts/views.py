from django.shortcuts import render
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .serializers import FreeBusyRequestSerializer
import requests
from allauth.socialaccount.models import SocialAccount, SocialToken
from rest_framework.response import Response
from .models import Profile, Location
from rest_framework import status
from django.contrib.auth import get_user_model
import traceback

"""
accounts/views.py

Contains custom authentication views, including Google OAuth login.
"""

User = get_user_model()


class CheckUserByEmail(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            email = request.query_params.get("email", "").strip()

            if not email:
                return Response(
                    {"exists": False, "error": "No email provided"}, status=400
                )

            exists = User.objects.filter(email__iexact=email).exists()

            return Response({"exists": exists})
        except Exception as e:
            return Response({"exists": False, "error": str(e)}, status=500)


class GoogleLogin(SocialLoginView):
    """
    Handles Google OAuth login for the When2Meet app using dj-rest-auth and allauth.
    """

    adapter_class = GoogleOAuth2Adapter
    serializer_class = None  # Will be set in get_serializer_class()
    
    def get_serializer_class(self):
        from .serializers import GoogleLoginSerializer
        return GoogleLoginSerializer
    
    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        # Ensure context is properly set
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs)
    
    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        context = super().get_serializer_context()
        context.update({
            'view': self,
            'request': self.request,
        })
        return context

    def post(self, request, *args, **kwargs):
        # Store the access token from the request for later use
        access_token = request.data.get('access_token')
        
        try:
            response = super().post(request, *args, **kwargs)
            
            # If login was successful and we have an authenticated user, store the social token
            if (response.status_code == 200 and hasattr(request, 'user') and 
                request.user.is_authenticated and access_token):
                
                try:
                    # Get the user's Google social account
                    google_account = SocialAccount.objects.filter(
                        user=request.user, provider='google'
                    ).first()
                    
                    if google_account:
                        # Get the Google OAuth app
                        from allauth.socialaccount.models import SocialApp
                        google_app = SocialApp.objects.filter(provider='google').first()
                        
                        if google_app:
                            # Check if token already exists
                            existing_token = SocialToken.objects.filter(
                                account=google_account, app=google_app
                            ).first()
                            
                            if existing_token:
                                existing_token.token = access_token
                                existing_token.token_secret = ''
                                existing_token.expires_at = None
                                existing_token.save()
                                print(f"Google social token updated for user: {request.user.email}")
                            else:
                                social_token = SocialToken.objects.create(
                                    app=google_app,
                                    account=google_account,
                                    token=access_token,
                                    token_secret='',
                                    expires_at=None
                                )
                                print(f"Google social token created for user: {request.user.email}")
                        
                except Exception as token_error:
                    print(f"Error storing social token: {token_error}")
            
            return response
            
        except Exception as e:
            print(f"Google login error: {e}")
            return Response(
                {"error": "Google login failed", "details": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProfileView(APIView):
    """
    API endpoint to get and update user profile information.
    Requires authentication.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Get the authenticated user's profile information.
        """
        try:
            profile = Profile.objects.get(user=request.user)
            return Response(
                {
                    "unique_id": profile.unique_id,
                    "username": request.user.username,
                    "email": request.user.email,
                    "name": profile.name,
                    "location": profile.location,
                }
            )
        except Exception as e:
            return Response(
                {"error": "Database error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request):
        """
        Update the authenticated user's profile information.
        """
        try:
            profile = Profile.objects.get(user=request.user)
            profile.name = request.data.get("name", profile.name)

            if "location" in request.data:
                location_id = request.data.get("location")
                if location_id is None:
                    profile.location = None
                else:
                    try:
                        location = Location.objects.get(id=location_id)
                        profile.location = location
                    except (Location.DoesNotExist, ValueError):
                        return Response(
                            {"error": "Invalid location ID"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )

            profile.save()
            return Response(
                {
                    "unique_id": profile.unique_id,
                    "name": profile.name,
                    "location": profile.location.id if profile.location else None,
                }
            )
        except Exception as e:
            return Response(
                {"error": "Database error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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
        serializer = FreeBusyRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        start = serializer.validated_data["start"]
        end = serializer.validated_data["end"]

        # Get user's Google access token
        try:
            social_account = SocialAccount.objects.get(
                user=request.user, provider="google"
            )
            social_token = SocialToken.objects.get(account=social_account)
        except (SocialAccount.DoesNotExist, SocialToken.DoesNotExist):
            return Response({"error": "Google account not connected"}, status=400)

        access_token = social_token.token

        # Call Google Calendar FreeBusy API
        url = "https://www.googleapis.com/calendar/v3/freeBusy"
        headers = {"Authorization": f"Bearer {access_token}"}
        data = {
            "timeMin": start.isoformat() + "Z",
            "timeMax": end.isoformat() + "Z",
            "items": [{"id": "primary"}],
        }
        resp = requests.post(url, headers=headers, json=data)
        if resp.status_code == 401:  # Unauthorized - likely expired/invalid token
            return Response(
                {
                    "error": "Google token expired or invalid. Please reconnect your Google account."
                },
                status=401,
            )
        elif resp.status_code != 200:
            return Response(
                {
                    "error": "Failed to fetch from Google Calendar",
                    "details": resp.json(),
                },
                status=resp.status_code,
            )

        freebusy = resp.json()
        # Returns the busy slots from "primary" calendar
        busy_slots = freebusy.get("calendars", {}).get("primary", {}).get("busy", [])
        return Response({"busy": busy_slots})
