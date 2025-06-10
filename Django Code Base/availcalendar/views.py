from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from allauth.socialaccount.models import SocialAccount, SocialToken
from accounts.serializers import FreeBusyRequestSerializer
from .tasks import sync_google_calendar_task, get_google_token, fetch_google_busy_slots


class GoogleCalendarSyncView(APIView):
    """
    GET → fetch busy slots from Google Calendar (no side‐effects)
    PUT → asynchronously fetch + persist busy slots as TimeSlot(source='google')
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Synchronously fetches busy slots for a preview.
        """
        serializer = FreeBusyRequestSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        start, end = validated_data["start"], validated_data["end"]
        # Allow selecting multiple calendars
        calendar_ids = validated_data.get("calendars", ["primary"])

        token = get_google_token(request.user.id)
        if not token:
            return Response({"error": "Google account not connected"},
                            status=status.HTTP_400_BAD_REQUEST)

        busy, error = fetch_google_busy_slots(start, end, token, calendar_ids)
        if error:
            return Response(
                {"error": "Failed to fetch from Google", "details": error},
                status=status.HTTP_502_BAD_GATEWAY # 502 is appropriate for upstream API errors
            )

        return Response({"busy": busy}, status=status.HTTP_200_OK)

    def put(self, request):
        """
        Initiates an asynchronous task to sync the calendar.
        """
        serializer = FreeBusyRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        sync_google_calendar_task.delay(
            user_id=request.user.id,
            start_iso=validated_data["start"].isoformat(),
            end_iso=validated_data["end"].isoformat(),
            calendar_ids=validated_data.get("calendars", ["primary"])
        )

        return Response(
            {"message": "Calendar synchronization has been initiated."},
            status=status.HTTP_202_ACCEPTED
        )