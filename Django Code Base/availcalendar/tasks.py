import requests
import logging
from dateutil.parser import isoparse
from celery import shared_task
from allauth.socialaccount.models import SocialAccount, SocialToken
from accounts.models import Profile
from .models import TimeSlot

# It's good practice to use a logger for background tasks
logger = logging.getLogger(__name__)

def get_google_token(user_id):
    """Helper function to retrieve a user's Google token."""
    try:
        profile = Profile.objects.get(user_id = user_id)
        acct = SocialAccount.objects.get(user = profile.user, provider = "google")
        return SocialToken.objects.get(account = acct).token
    except (Profile.DoesNotExist, SocialAccount.DoesNotExist, SocialToken.DoesNotExist):
        logger.warning(f"Could not retrieve Google token for user_id: {user_id}")
        return None

def fetch_google_busy_slots(start, end, token, calendar_ids):
    """
    Helper function to fetch busy slots from Google Calendar API with robust error handling.
    """
    url = "https://www.googleapis.com/calendar/v3/freeBusy"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "timeMin": start.isoformat(),
        "timeMax": end.isoformat(),
        "items": [{"id": calendar_id} for calendar_id in calendar_ids]
    }
    
    try:
        resp = requests.post(url, headers = headers, json = payload)
        resp.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch from Google Calendar API: {e}")
        return None, f"Request to Google API failed: {e}"

    data = resp.json()
    
    # Check the response structure
    calendars_data = data.get("calendars")
    if not calendars_data:
        logger.warning("Google API response missing 'calendars' key.")
        return None, "Invalid response structure from Google API."

    busy_slots = []
    for calendar_id in calendar_ids:
        calendar_info = calendars_data.get(calendar_id)
        if not calendar_info:
            logger.warning(f"Response missing data for calendar: {calendar_id}")
            continue # Move to the next calendar
            
        if "errors" in calendar_info:
            logger.error(f"Google API returned errors for calendar {calendar_id}: {calendar_info['errors']}")
            continue

        busy_slots.extend(calendar_info.get("busy", []))
        
    return busy_slots, None


@shared_task
def sync_google_calendar_task(user_id, start_iso, end_iso, calendar_ids):
    """
    Celery task to fetch busy slots from Google Calendar and persist them to the database.
    """
    token = get_google_token(user_id)
    if not token:
        return {"status": "Failed", "error": "Google account not connected or token not found."}

    start = isoparse(start_iso)
    end = isoparse(end_iso)

    busy, error = fetch_google_busy_slots(start, end, token, calendar_ids)
    if error:
        return {"status": "Failed", "error": error}

    try:
        profile = Profile.objects.get(user_id = user_id)
        
        # 3. Delete stale TimeSlots for the given period before adding new ones
        TimeSlot.objects.filter(
            user = profile,
            start__gte = start,
            end__lte = end,
            source = "google"
        ).delete()

        # Persist new TimeSlots
        created_count = 0
        for period in busy:
            st = isoparse(period["start"])
            en = isoparse(period["end"])
            _, was_created = TimeSlot.objects.get_or_create(
                user = profile,
                start = st,
                end = en,
                source = "google"
            )
            if was_created:
                created_count += 1
        
        logger.info(f"Successfully synced {len(busy)} slots for user {user_id}, {created_count} were new.")
        return {"status": "Success", "imported_slots": len(busy), "new_slots": created_count}

    except Profile.DoesNotExist:
        logger.error(f"Profile not found for user_id: {user_id}")
        return {"status": "Failed", "error": "User profile not found."}
    except Exception as e:
        logger.error(f"Database error during sync for user {user_id}: {e}")
        return {"status": "Failed", "error": "An unexpected database error occurred."}