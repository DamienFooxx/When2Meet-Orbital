import requests
import logging
from dateutil.parser import isoparse
from datetime import datetime, date, time
from celery import shared_task
from allauth.socialaccount.models import SocialAccount, SocialToken
from accounts.models import Profile
from .models import CalendarEntry

logger = logging.getLogger(__name__)


def get_google_token(user_id):
    """Helper function to retrieve a user's Google token."""
    try:
        profile = Profile.objects.get(user_id=user_id)
        acct = SocialAccount.objects.get(user=profile.user, provider="google")
        return SocialToken.objects.get(account=acct).token
    except (Profile.DoesNotExist, SocialAccount.DoesNotExist, SocialToken.DoesNotExist):
        logger.warning(f"Could not retrieve Google token for user_id: {user_id}")
        return None


def fetch_google_busy_slots(start, end, token, calendar_ids):
    """
    Helper function to fetch busy slots from Google Calendar API using Events API.
    This handles all-day events better than FreeBusy API.
    """
    busy_slots = []
    
    for calendar_id in calendar_ids:
        url = f"https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events"
        headers = {"Authorization": f"Bearer {token}"}
        params = {
            "timeMin": start.isoformat() + "Z" if start.tzinfo is None else start.isoformat(),
            "timeMax": end.isoformat() + "Z" if end.tzinfo is None else end.isoformat(),
            "singleEvents": True,
            "orderBy": "startTime"
        }

        try:
            resp = requests.get(url, headers=headers, params=params)
            resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch from Google Calendar API: {e}")
            return None, f"Request to Google API failed: {e}"

        data = resp.json()
        events = data.get("items", [])
        
        for event in events:
            # Skip events that are not busy (like available/free time blocks)
            if event.get("transparency") == "transparent":
                continue
                
            start_info = event.get("start", {})
            end_info = event.get("end", {})
            
            # Handle all-day events
            if "date" in start_info:
                # All-day event
                event_start = start_info["date"] + "T00:00:00"
                event_end = end_info["date"] + "T00:00:00"  # End date is exclusive for all-day events
            else:
                # Timed event
                event_start = start_info.get("dateTime")
                event_end = end_info.get("dateTime")
            
            if event_start and event_end:
                busy_slots.append({
                    "start": event_start,
                    "end": event_end
                })

    return busy_slots, None


@shared_task
def sync_google_calendar_task(user_id, start_iso, end_iso, calendar_ids):
    """
    Celery task to fetch busy slots from Google Calendar and persist them to the database.
    """
    token = get_google_token(user_id)
    if not token:
        return {
            "status": "Failed",
            "error": "Google account not connected or token not found.",
        }

    start = isoparse(start_iso)
    end = isoparse(end_iso)

    busy, error = fetch_google_busy_slots(start, end, token, calendar_ids)
    if error:
        return {"status": "Failed", "error": error}

    try:
        profile = Profile.objects.get(user_id=user_id)

        # Delete stale CalendarEntries for the given period before adding new ones
        CalendarEntry.objects.filter(
            user=profile, 
            start_date__gte=start.date(), 
            end_date__lte=end.date(), 
            source="google"
        ).delete()

        # Persist new CalendarEntries
        created_count = 0
        for period in busy:
            st = isoparse(period["start"])
            en = isoparse(period["end"])
            
            # Extract date and time components
            start_date = st.date()
            start_time = st.time()
            end_date = en.date()
            end_time = en.time()
            
            # Calculate duration in minutes
            duration = int((en - st).total_seconds() / 60)
            
            _, was_created = CalendarEntry.objects.get_or_create(
                user=profile, 
                start_date=start_date,
                start_time=start_time,
                end_date=end_date,
                end_time=end_time,
                source="google",
                defaults={
                    'title': 'Google Calendar Event',
                    'description': 'Imported from Google Calendar',
                    'duration': duration,
                }
            )
            if was_created:
                created_count += 1

        logger.info(
            f"Successfully synced {len(busy)} slots for user {user_id}, {created_count} were new."
        )
        return {
            "status": "Success",
            "imported_slots": len(busy),
            "new_slots": created_count,
        }

    except Profile.DoesNotExist:
        logger.error(f"Profile not found for user_id: {user_id}")
        return {"status": "Failed", "error": "User profile not found."}
    except Exception as e:
        logger.error(f"Database error during sync for user {user_id}: {e}")
        return {"status": "Failed", "error": "An unexpected database error occurred."}
