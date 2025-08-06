from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, time, timedelta, datetime
from unittest.mock import patch, MagicMock
from availcalendar.models import (
    TimeSlot,
    CalendarEntry,
    CalendarIntegration,
    ManualAvailability,
    Reminder,
)
from availcalendar.views import (
    TimeSlotViewSet,
    CalendarEntryViewSet,
    CalendarIntegrationViewSet,
    ManualAvailabilityViewSet,
    ReminderViewSet,
    GoogleCalendarSyncView,
    month_availability,
)
from availcalendar.tasks import (
    get_google_token,
    fetch_google_busy_slots,
    sync_google_calendar_task,
)
from availcalendar.serializers import (
    TimeSlotSerializer,
    CalendarEntrySerializer,
    CalendarIntegrationSerializer,
    ManualAvailabilitySerializer,
    ReminderSerializer,
)
from accounts.models import Profile, Location
from events.models import Event, EventParticipant
from allauth.socialaccount.models import SocialAccount, SocialToken, SocialApp
from groups.models import GroupMembership, Group
import requests


class BaseCalendarTestCase(APITestCase):
    """
    Test Cases for Event model
    """

    @patch("accounts.models.geolocator.geocode")
    def setUp(self, mock_geocode):
        # Mock geocode
        mock_location = MagicMock()
        mock_location.latitude = 1.3521
        mock_location.longitude = 103.8198
        mock_geocode.return_value = mock_location
        # Create a location
        self.location = Location.objects.create(
            postalcode="117417",
            city="Singapore",
            country="SG",
            street_address="13 Computing Drive",
        )
        # Create users and profiles
        self.user1 = User.objects.create_user(username="user1", password="pass123")
        self.user2 = User.objects.create_user(username="user2", password="pass123")
        self.profile1 = self.user1.profile
        self.profile1.name = "Test User 1"
        self.profile1.save()
        self.profile2 = self.user2.profile
        self.profile2.name = "Test User 2"
        self.profile2.save()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)


class TimeSlotTestCase(BaseCalendarTestCase):
    def setUp(self):
        super().setUp()
        self.event = Event.objects.create(
            title="Event",
            description="",
            creator=self.profile1,
            location_id=self.location,
        )
        EventParticipant.objects.create(event=self.event, participant=self.profile1)
        self.timeslot_url = reverse("timeslot-list")

    def test_create_valid_timeslot(self):
        data = {
            "event": self.event.pk,
            "user": self.profile1.pk,
            "start_date": "2024-01-01",
            "start_time": "10:00",
            "end_date": "2024-01-01",
            "end_time": "10:15",
            "duration": 15,
            "status": "not confirmed",
        }
        response = self.client.post(self.timeslot_url, data, format="json")
        # print("RESPONSE DATA:", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invalid_timeslot_interval(self):
        start = datetime.now().replace(minute=0, second=0, microsecond=0)
        end = start + timedelta(minutes=10)
        data = {
            "event": self.event.pk,
            "user": self.profile1.pk,
            "start_date": start.date().isoformat(),
            "start_time": start.time().isoformat(timespec="minutes"),
            "end_date": end.date().isoformat(),
            "end_time": end.time().isoformat(timespec="minutes"),
            "duration": 10,
            "status": "not confirmed",
        }
        response = self.client.post(self.timeslot_url, data, format="json")
        # print("RESPONSE DATA:", response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invalid_timeslot_boundary(self):
        start = datetime.now().replace(minute=7, second=0, microsecond=0)
        end = start + timedelta(minutes=15)
        data = {
            "event": self.event.pk,
            "user": self.profile1.pk,
            "start_date": start.date().isoformat(),
            "start_time": start.time().isoformat(timespec="minutes"),
            "end_date": end.date().isoformat(),
            "end_time": end.time().isoformat(timespec="minutes"),
            "duration": 15,
            "status": "not confirmed",
        }
        response = self.client.post(self.timeslot_url, data, format="json")
        # print("RESPONSE DATA:", response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CalendarEntryTestCase(BaseCalendarTestCase):
    def setUp(self):
        super().setUp()
        self.event = Event.objects.create(
            title="Event",
            description="",
            creator=self.profile1,
            location_id=self.location,
        )
        EventParticipant.objects.create(event=self.event, participant=self.profile1)
        self.calendar_url = reverse("calendar-entry-list")

    def test_create_valid_calendar_entry(self):
        data = {
            "title": "Meeting",
            "description": "Discuss project",
            "start_date": "2024-01-01",
            "start_time": "10:00",
            "end_date": "2024-01-01",
            "end_time": "10:15",
            "duration": 15,
            "source": "manual",
            "location": self.location.pk,
            "user": self.profile1.pk,
            "event": self.event.pk,
        }
        response = self.client.post(self.calendar_url, data, format="json")
        # print("RESPONSE DATA:", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Meeting")

    def test_create_invalid_calendar_entry_short(self):
        start = datetime.now().replace(minute=0, second=0, microsecond=0)
        end = start + timedelta(minutes=10)
        data = {
            "title": "Short Meeting",
            "description": "Too short",
            "start_date": start.date().isoformat(),
            "start_time": start.time().isoformat(timespec="minutes"),
            "end_date": end.date().isoformat(),
            "end_time": end.time().isoformat(timespec="minutes"),
            "duration": 10,
            "source": "manual",
            "location": self.location.pk,
            "user": self.profile1.pk,
            "event": self.event.pk,
        }
        response = self.client.post(self.calendar_url, data, format="json")
        # print("RESPONSE DATA:", response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invalid_calendar_entry_start_after_end(self):
        start = datetime.now().replace(minute=0, second=0, microsecond=0)
        end = start - timedelta(minutes=15)
        data = {
            "title": "Backwards Meeting",
            "description": "Start after end",
            "start_date": start.date().isoformat(),
            "start_time": start.time().isoformat(timespec="minutes"),
            "end_date": end.date().isoformat(),
            "end_time": end.time().isoformat(timespec="minutes"),
            "duration": -15,
            "source": "manual",
            "location": self.location.pk,
            "user": self.profile1.pk,
            "event": self.event.pk,
        }
        response = self.client.post(self.calendar_url, data, format="json")
        # print("RESPONSE DATA:", response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ManualAvailabilityTestCase(BaseCalendarTestCase):
    def setUp(self):
        super().setUp()
        self.manual_url = reverse("manual-availability-list")

    def test_create_manual_availability_valid(self):
        data = {
            "start_date": "2024-01-01",
            "start_time": "10:00",
            "end_date": "2024-01-01",
            "end_time": "10:30",
            "duration": 30,
            "freq": "DAILY",
            "interval": 1,
            "by_day": ["MO", "WE"],
            "count": 2,
        }
        response = self.client.post(self.manual_url, data, format="json")
        # print("RESPONSE DATA:", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("recurrence", response.data)

    def test_create_manual_availability_invalid_interval(self):
        start = datetime.now().replace(minute=0, second=0, microsecond=0)
        end = start + timedelta(minutes=10)
        data = {
            "start_date": start.date().isoformat(),
            "start_time": start.time().isoformat(timespec="minutes"),
            "end_date": end.date().isoformat(),
            "end_time": end.time().isoformat(timespec="minutes"),
            "duration": 10,
            "freq": "DAILY",
            "interval": 1,
        }
        response = self.client.post(self.manual_url, data, format="json")
        # print("RESPONSE DATA:", response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_availability_start_after_end(self):
        start = datetime.now().replace(minute=0, second=0, microsecond=0)
        end = start - timedelta(minutes=15)
        data = {
            "start_date": start.date().isoformat(),
            "start_time": start.time().isoformat(timespec="minutes"),
            "end_date": end.date().isoformat(),
            "end_time": end.time().isoformat(timespec="minutes"),
            "duration": -15,
            "freq": "DAILY",
            "interval": 1,
        }
        response = self.client.post(self.manual_url, data, format="json")
        # print("RESPONSE DATA:", response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ReminderTestCase(BaseCalendarTestCase):
    def setUp(self):
        super().setUp()
        self.event = Event.objects.create(
            title="Event",
            description="",
            creator=self.profile1,
            location_id=self.location,
        )
        EventParticipant.objects.create(event=self.event, participant=self.profile1)
        self.calendar_entry = CalendarEntry.objects.create(
            title="Meeting",
            description="Discuss project",
            start_date=datetime.now().date(),
            start_time=datetime.now().time(),
            end_date=(datetime.now() + timedelta(minutes=15)).date(),
            end_time=(datetime.now() + timedelta(minutes=15)).time(),
            duration=15,
            source="manual",
            location_id=self.location.pk,
            user_id=self.profile1.pk,
            event_id=self.event.pk,
        )
        self.reminder_url = reverse("reminder-list")

    def test_create_reminder(self):
        remind_at = datetime.now() + timedelta(minutes=5)
        data = {
            "remind_at": remind_at.isoformat(),
            "calendar_entry": self.calendar_entry.pk,
            "user": self.profile1.pk,
        }
        response = self.client.post(self.reminder_url, data, format="json")
        # print("RESPONSE DATA:", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_reminder_exclusive_to_user(self):
        remind_at = datetime.now() + timedelta(minutes=5)
        data = {
            "remind_at": remind_at.isoformat(),
            "calendar_entry": self.calendar_entry.pk,
            "user": self.profile1.pk,
        }
        self.client.post(self.reminder_url, data, format="json")
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(self.reminder_url)
        # print("RESPONSE DATA:", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


class TasksTestCase(APITestCase):
    """
    Test suite for availcalendar tasks
    """

    def setUp(self):
        # Mock geocode
        self.mock_geocode = patch("accounts.models.geolocator.geocode").start()
        mock_location = MagicMock()
        mock_location.latitude = 1.3521
        mock_location.longitude = 103.8198
        self.mock_geocode.return_value = mock_location

        # Create test user and profile
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.profile = Profile.objects.get(user=self.user)
        
        # Create social app
        self.social_app = SocialApp.objects.create(
            provider='google',
            name='Google',
            client_id='test_client_id',
            secret='test_secret'
        )
        
        # Create social account
        self.social_account = SocialAccount.objects.create(
            user=self.user,
            provider='google',
            uid='test_uid'
        )
        
        # Create social token
        self.social_token = SocialToken.objects.create(
            account=self.social_account,
            app=self.social_app,
            token='test_token'
        )

    def tearDown(self):
        patch.stopall()

    def test_get_google_token_success(self):
        """Test successful token retrieval"""
        token = get_google_token(self.user.id)
        self.assertEqual(token, 'test_token')

    def test_get_google_token_no_profile(self):
        """Test token retrieval when profile doesn't exist"""
        # Delete the profile
        self.profile.delete()
        
        token = get_google_token(self.user.id)
        self.assertIsNone(token)

    def test_get_google_token_no_social_account(self):
        """Test token retrieval when social account doesn't exist"""
        # Delete the social account
        self.social_account.delete()
        
        token = get_google_token(self.user.id)
        self.assertIsNone(token)

    def test_get_google_token_no_token(self):
        """Test token retrieval when token doesn't exist"""
        # Delete the token
        self.social_token.delete()
        
        token = get_google_token(self.user.id)
        self.assertIsNone(token)

    @patch('availcalendar.tasks.requests.get')
    def test_fetch_google_busy_slots_success(self, mock_get):
        """Test successful fetch of busy slots"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "items": [
                {
                    "start": {"dateTime": "2024-01-01T10:00:00Z"},
                    "end": {"dateTime": "2024-01-01T11:00:00Z"},
                    "transparency": "opaque"
                },
                {
                    "start": {"dateTime": "2024-01-01T14:00:00Z"},
                    "end": {"dateTime": "2024-01-01T15:00:00Z"},
                    "transparency": "opaque"
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        start = datetime(2024, 1, 1, 0, 0, 0)
        end = datetime(2024, 1, 1, 23, 59, 59)
        calendar_ids = ["primary"]
        
        busy_slots, error = fetch_google_busy_slots(start, end, "test_token", calendar_ids)
        
        self.assertIsNone(error)
        self.assertEqual(len(busy_slots), 2)
        self.assertEqual(busy_slots[0]["start"], "2024-01-01T10:00:00Z")
        self.assertEqual(busy_slots[0]["end"], "2024-01-01T11:00:00Z")

    @patch('availcalendar.tasks.requests.get')
    def test_fetch_google_busy_slots_all_day_events(self, mock_get):
        """Test fetching busy slots with all-day events"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "items": [
                {
                    "start": {"date": "2024-01-01"},
                    "end": {"date": "2024-01-02"},
                    "transparency": "opaque"
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        start = datetime(2024, 1, 1, 0, 0, 0)
        end = datetime(2024, 1, 1, 23, 59, 59)
        calendar_ids = ["primary"]
        
        busy_slots, error = fetch_google_busy_slots(start, end, "test_token", calendar_ids)
        
        self.assertIsNone(error)
        self.assertEqual(len(busy_slots), 1)
        self.assertEqual(busy_slots[0]["start"], "2024-01-01T00:00:00")
        self.assertEqual(busy_slots[0]["end"], "2024-01-02T00:00:00")

    @patch('availcalendar.tasks.requests.get')
    def test_fetch_google_busy_slots_transparent_events(self, mock_get):
        """Test that transparent events are skipped"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "items": [
                {
                    "start": {"dateTime": "2024-01-01T10:00:00Z"},
                    "end": {"dateTime": "2024-01-01T11:00:00Z"},
                    "transparency": "transparent"
                },
                {
                    "start": {"dateTime": "2024-01-01T14:00:00Z"},
                    "end": {"dateTime": "2024-01-01T15:00:00Z"},
                    "transparency": "opaque"
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        start = datetime(2024, 1, 1, 0, 0, 0)
        end = datetime(2024, 1, 1, 23, 59, 59)
        calendar_ids = ["primary"]
        
        busy_slots, error = fetch_google_busy_slots(start, end, "test_token", calendar_ids)
        
        self.assertIsNone(error)
        self.assertEqual(len(busy_slots), 1)  # Only the opaque event
        self.assertEqual(busy_slots[0]["start"], "2024-01-01T14:00:00Z")

    @patch('availcalendar.tasks.requests.get')
    def test_fetch_google_busy_slots_multiple_calendars(self, mock_get):
        """Test fetching busy slots from multiple calendars"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "items": [
                {
                    "start": {"dateTime": "2024-01-01T10:00:00Z"},
                    "end": {"dateTime": "2024-01-01T11:00:00Z"},
                    "transparency": "opaque"
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        start = datetime(2024, 1, 1, 0, 0, 0)
        end = datetime(2024, 1, 1, 23, 59, 59)
        calendar_ids = ["primary", "work"]
        
        busy_slots, error = fetch_google_busy_slots(start, end, "test_token", calendar_ids)
        
        self.assertIsNone(error)
        self.assertEqual(len(busy_slots), 2)  # One event from each calendar
        self.assertEqual(mock_get.call_count, 2)  # Called twice for two calendars

    @patch('availcalendar.tasks.requests.get')
    def test_fetch_google_busy_slots_api_error(self, mock_get):
        """Test handling of API errors"""
        start = datetime(2024, 1, 1, 10, 0)
        end = datetime(2024, 1, 1, 11, 0)
        calendar_ids = ["primary"]
        
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "API Error"}
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("400 Client Error")
        mock_get.return_value = mock_response
        
        busy_slots, error = fetch_google_busy_slots(start, end, "test_token", calendar_ids)
        
        self.assertEqual(busy_slots, None)
        self.assertIsNotNone(error)
        self.assertIn("Request to Google API failed", error)

    @patch('availcalendar.tasks.fetch_google_busy_slots')
    @patch('availcalendar.tasks.get_google_token')
    def test_sync_google_calendar_task_success(self, mock_get_token, mock_fetch_busy):
        """Test successful calendar sync task"""
        mock_get_token.return_value = "test_token"
        mock_fetch_busy.return_value = (
            [
                {"start": "2024-01-01T10:00:00Z", "end": "2024-01-01T11:00:00Z"}
            ],
            None
        )
        
        start_iso = "2024-01-01T00:00:00Z"
        end_iso = "2024-01-01T23:59:59Z"
        calendar_ids = ["primary"]
        
        result = sync_google_calendar_task(self.user.id, start_iso, end_iso, calendar_ids)
        
        self.assertEqual(result["status"], "Success")
        self.assertIn("new_slots", result)

    @patch('availcalendar.tasks.get_google_token')
    def test_sync_google_calendar_task_no_token(self, mock_get_token):
        """Test calendar sync task when no token is available"""
        mock_get_token.return_value = None
        
        start_iso = "2024-01-01T00:00:00Z"
        end_iso = "2024-01-01T23:59:59Z"
        calendar_ids = ["primary"]
        
        result = sync_google_calendar_task(self.user.id, start_iso, end_iso, calendar_ids)
        
        self.assertEqual(result["status"], "Failed")
        self.assertIn("Google account not connected", result["error"])

    @patch('availcalendar.tasks.fetch_google_busy_slots')
    @patch('availcalendar.tasks.get_google_token')
    def test_sync_google_calendar_task_fetch_error(self, mock_get_token, mock_fetch_busy):
        """Test calendar sync task when fetch fails"""
        mock_get_token.return_value = "test_token"
        mock_fetch_busy.return_value = (None, "API Error")
        
        start_iso = "2024-01-01T00:00:00Z"
        end_iso = "2024-01-01T23:59:59Z"
        calendar_ids = ["primary"]
        
        result = sync_google_calendar_task(self.user.id, start_iso, end_iso, calendar_ids)
        
        self.assertEqual(result["status"], "Failed")
        self.assertEqual(result["error"], "API Error")

    @patch('availcalendar.tasks.fetch_google_busy_slots')
    @patch('availcalendar.tasks.get_google_token')
    def test_sync_google_calendar_task_database_error(self, mock_get_token, mock_fetch_busy):
        """Test calendar sync task when database operations fail"""
        mock_get_token.return_value = "test_token"
        mock_fetch_busy.return_value = (
            [
                {"start": "2024-01-01T10:00:00Z", "end": "2024-01-01T11:00:00Z"}
            ],
            None
        )
        
        # Delete the profile to cause a database error
        self.profile.delete()
        
        start_iso = "2024-01-01T00:00:00Z"
        end_iso = "2024-01-01T23:59:59Z"
        calendar_ids = ["primary"]
        
        result = sync_google_calendar_task(self.user.id, start_iso, end_iso, calendar_ids)
        
        self.assertEqual(result["status"], "Failed")
        self.assertIn("error", result)

    @patch('availcalendar.tasks.fetch_google_busy_slots')
    @patch('availcalendar.tasks.get_google_token')
    def test_sync_google_calendar_task_creates_entries(self, mock_get_token, mock_fetch_busy):
        """Test that calendar sync task creates CalendarEntry objects"""
        mock_get_token.return_value = "test_token"
        mock_fetch_busy.return_value = (
            [
                {"start": "2024-01-01T10:00:00Z", "end": "2024-01-01T11:00:00Z"},
                {"start": "2024-01-01T14:00:00Z", "end": "2024-01-01T15:00:00Z"}
            ],
            None
        )
        
        start_iso = "2024-01-01T00:00:00Z"
        end_iso = "2024-01-01T23:59:59Z"
        calendar_ids = ["primary"]
        
        # Check initial count
        initial_count = CalendarEntry.objects.count()
        
        result = sync_google_calendar_task(self.user.id, start_iso, end_iso, calendar_ids)
        
        # Check that entries were created
        final_count = CalendarEntry.objects.count()
        self.assertEqual(final_count, initial_count + 2)
        
        self.assertEqual(result["status"], "Success")
        self.assertEqual(result["new_slots"], 2)

    @patch('availcalendar.tasks.fetch_google_busy_slots')
    @patch('availcalendar.tasks.get_google_token')
    def test_sync_google_calendar_task_deletes_stale_entries(self, mock_get_token, mock_fetch_busy):
        """Test that calendar sync task deletes stale entries"""
        mock_get_token.return_value = "test_token"
        mock_fetch_busy.return_value = ([], None)
        
        # Create some existing entries
        CalendarEntry.objects.create(
            user=self.profile,
            start_date=date(2024, 1, 1),
            start_time=time(10, 0),
            end_date=date(2024, 1, 1),
            end_time=time(11, 0),
            source="google"
        )
        CalendarEntry.objects.create(
            user=self.profile,
            start_date=date(2024, 1, 1),
            start_time=time(14, 0),
            end_date=date(2024, 1, 1),
            end_time=time(15, 0),
            source="google"
        )
        
        start_iso = "2024-01-01T00:00:00Z"
        end_iso = "2024-01-01T23:59:59Z"
        calendar_ids = ["primary"]
        
        result = sync_google_calendar_task(self.user.id, start_iso, end_iso, calendar_ids)
        
        # Check that stale entries were deleted
        self.assertEqual(CalendarEntry.objects.count(), 0)
        self.assertEqual(result["status"], "Success")
        self.assertEqual(result["new_slots"], 0)


class AvailCalendarViewsTestCase(APITestCase):
    """
    Test suite for availcalendar views
    """

    def setUp(self):
        # Mock geocode
        self.mock_geocode = patch("accounts.models.geolocator.geocode").start()
        mock_location = MagicMock()
        mock_location.latitude = 1.3521
        mock_location.longitude = 103.8198
        self.mock_geocode.return_value = mock_location

        # Create test users
        self.user1 = User.objects.create_user(
            username="testuser1",
            email="test1@gmail.com",
            password="testpass123",
        )
        self.user2 = User.objects.create_user(
            username="testuser2",
            email="test2@gmail.com",
            password="testpass123",
        )
        self.user3 = User.objects.create_user(
            username="testuser3",
            email="test3@gmail.com",
            password="testpass123",
        )

        # Get their profiles
        self.profile1 = Profile.objects.get(user=self.user1)
        self.profile2 = Profile.objects.get(user=self.user2)
        self.profile3 = Profile.objects.get(user=self.user3)

        # Create location
        self.location = Location.objects.create(
            postalcode="117417",
            city="Singapore",
            country="SG",
            street_address="13 Computing Drive",
        )

        # Create event
        self.event = Event.objects.create(
            title="Test Event",
            description="Test Description",
            creator=self.profile1,
            location_id=self.location,
        )

        # Create event participant
        EventParticipant.objects.create(
            event=self.event,
            participant=self.profile1
        )

        # Set up API client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)

    def tearDown(self):
        patch.stopall()

    def test_timeslot_viewset_get_queryset(self):
        """Test TimeSlotViewSet queryset filtering"""
        url = reverse("timeslot-list")
        
        # Create a location and group for the event
        location = Location.objects.create(
            street_address="123 Test St",
            city="Test City",
            country="SG",
            postalcode="12345"
        )
        
        group = Group.objects.create(
            name="Test Group",
            description="Test Description",
            creator=self.user1.profile
        )
        
        # Create an event for the user
        event = Event.objects.create(
            title="Test Event",
            creator=self.user1.profile,
            location_id=location,
            group=group
        )
        
        # Add user1 as participant to the event
        EventParticipant.objects.create(
            event=event,
            participant=self.user1.profile
        )
        
        # Create a timeslot for the event
        TimeSlot.objects.create(
            event_id=event,
            user=self.user1.profile,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 1),
            start_time=time(10, 0),
            end_time=time(11, 0)
        )
        
        # Create another timeslot for a different event
        event2 = Event.objects.create(
            title="Test Event 2",
            creator=self.user1.profile,
            location_id=location,
            group=group
        )
        
        # Add user2 as participant to event2
        EventParticipant.objects.create(
            event=event2,
            participant=self.user2.profile
        )
        
        TimeSlot.objects.create(
            event_id=event2,
            user=self.user2.profile,
            start_date=date(2024, 1, 2),
            end_date=date(2024, 1, 2),
            start_time=time(14, 0),
            end_time=time(15, 0)
        )
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_timeslot_viewset_create(self):
        """Test TimeSlotViewSet create"""
        # Create a location and group for the event
        location = Location.objects.create(
            street_address="123 Test St",
            city="Test City",
            country="SG",
            postalcode="12345"
        )
        
        group = Group.objects.create(
            name="Test Group",
            description="Test Description",
            creator=self.user1.profile
        )
        
        # Create an event for the user
        event = Event.objects.create(
            title="Test Event",
            creator=self.user1.profile,
            location_id=location,
            group=group
        )
        
        # Add user1 as participant to the event
        EventParticipant.objects.create(
            event=event,
            participant=self.user1.profile
        )
        
        url = reverse("timeslot-list")
        data = {
            "event": event.id,
            "user": self.user1.profile.unique_id,
            "start_date": "2024-01-01",
            "start_time": "10:00:00",
            "end_date": "2024-01-01",
            "end_time": "11:00:00",
            "duration": 60,
            "status": "not confirmed"
        }
        
        response = self.client.post(url, data, format="json")
        
        if response.status_code != status.HTTP_201_CREATED:
            print(f"Validation error: {response.data}")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TimeSlot.objects.count(), 1)

    def test_timeslot_viewset_other_user_event(self):
        """Test TimeSlotViewSet queryset filtering for other user's events"""
        url = reverse("timeslot-list")
        
        # Create a location and group for the event
        location = Location.objects.create(
            street_address="789 Third St",
            city="Third City",
            country="CA",
            postalcode="34567"
        )
        
        group = Group.objects.create(
            name="Test Group 2",
            description="Test Description 2",
            creator=self.user2.profile
        )
        
        # Create an event for user2
        event = Event.objects.create(
            title="Test Event 3",
            creator=self.user2.profile,
            location_id=location,
            group=group
        )
        
        # Add user1 as participant to the event
        EventParticipant.objects.create(
            event=event,
            participant=self.user1.profile
        )
        
        # Create a timeslot for the event
        TimeSlot.objects.create(
            event_id=event,
            user=self.user2.profile,
            start_date=date(2024, 1, 3),
            end_date=date(2024, 1, 3),
            start_time=time(16, 0),
            end_time=time(17, 0)
        )
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_calendar_entry_viewset_get_queryset(self):
        """Test CalendarEntryViewSet queryset filtering"""
        # Create calendar entry for user1
        entry = CalendarEntry.objects.create(
            user=self.profile1,
            title="Test Entry",
            start_date=date(2024, 1, 1),
            start_time=time(10, 0),
            end_date=date(2024, 1, 1),
            end_time=time(11, 0),
            source="manual"
        )

        url = reverse("calendar-entry-list")
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], entry.id)

    def test_calendar_entry_viewset_create(self):
        """Test CalendarEntryViewSet create"""
        # Create a location and group for the event
        location = Location.objects.create(
            street_address="123 Test St",
            city="Test City",
            country="SG",
            postalcode="12345"
        )
        
        group = Group.objects.create(
            name="Test Group",
            description="Test Description",
            creator=self.user1.profile
        )
        
        # Create an event for the user
        event = Event.objects.create(
            title="Test Event",
            creator=self.user1.profile,
            location_id=location,
            group=group
        )
        
        # Add user1 as participant to the event
        EventParticipant.objects.create(
            event=event,
            participant=self.user1.profile
        )
        
        url = reverse("calendar-entry-list")
        data = {
            "title": "Test Calendar Entry",
            "description": "Test Description",
            "start_date": "2024-01-01",
            "start_time": "10:00:00",
            "end_date": "2024-01-01",
            "end_time": "11:00:00",
            "duration": 60,
            "source": "manual",
            "google_event_id": "test_event_id",
            "location": location.id,
            "user": self.user1.profile.unique_id,
            "event": event.id
        }
        
        response = self.client.post(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CalendarEntry.objects.count(), 1)

    def test_calendar_entry_viewset_other_user_entries(self):
        """Test CalendarEntryViewSet doesn't show other user's entries"""
        # Create calendar entry for user2
        CalendarEntry.objects.create(
            user=self.profile2,
            title="User2 Entry",
            start_date=date(2024, 1, 1),
            start_time=time(10, 0),
            end_date=date(2024, 1, 1),
            end_time=time(11, 0),
            source="manual"
        )

        url = reverse("calendar-entry-list")
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)  # Should not see user2's entries

    def test_calendar_integration_viewset_get(self):
        """Test CalendarIntegrationViewSet get method"""
        url = reverse("calendar-integration-list")
        
        # Create a calendar integration
        CalendarIntegration.objects.create(
            user=self.user1.profile,
            provider="google",
            external_id="test_id",
            access_token="test_token",
            token_expiry=timezone.now() + timedelta(hours=1)
        )
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_calendar_integration_viewset_no_integration(self):
        """Test CalendarIntegrationViewSet when no integration exists"""
        url = reverse("calendar-integration-list")
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_manual_availability_viewset_get_queryset(self):
        """Test ManualAvailabilityViewSet queryset filtering"""
        # Create manual availability for user1
        availability = ManualAvailability.objects.create(
            user=self.profile1,
            start_date=date(2024, 1, 1),
            start_time=time(10, 0),
            end_date=date(2024, 1, 1),
            end_time=time(11, 0),
            duration=60
        )

        url = reverse("manual-availability-list")
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], availability.id)

    def test_manual_availability_viewset_create(self):
        """Test ManualAvailabilityViewSet create"""
        url = reverse("manual-availability-list")
        data = {
            "start_date": "2024-01-01",
            "start_time": "10:00:00",
            "end_date": "2024-01-01",
            "end_time": "11:00:00",
            "duration": 60,
            "freq": "DAILY",
            "interval": 1,
            "by_day": ["MO", "TU", "WE", "TH", "FR"],
            "until": "2024-01-31T23:59:59Z"
        }
        
        response = self.client.post(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ManualAvailability.objects.count(), 1)

    def test_manual_availability_viewset_other_user_availabilities(self):
        """Test ManualAvailabilityViewSet doesn't show other user's availabilities"""
        # Create manual availability for user2
        ManualAvailability.objects.create(
            user=self.profile2,
            start_date=date(2024, 1, 1),
            start_time=time(10, 0),
            end_date=date(2024, 1, 1),
            end_time=time(11, 0),
            duration=60
        )

        url = reverse("manual-availability-list")
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)  # Should not see user2's availabilities

    def test_reminder_viewset_get_queryset(self):
        """Test ReminderViewSet queryset filtering"""
        # Create calendar entry first
        entry = CalendarEntry.objects.create(
            user=self.profile1,
            title="Test Entry",
            start_date=date(2024, 1, 1),
            start_time=time(10, 0),
            end_date=date(2024, 1, 1),
            end_time=time(11, 0),
            source="manual"
        )
        
        # Create reminder for user1
        reminder = Reminder.objects.create(
            user_id=self.profile1,
            remind_at=datetime(2024, 1, 1, 10, 0, 0),
            calendar_entry_id=entry
        )

        url = reverse("reminder-list")
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], reminder.id)

    def test_reminder_viewset_create(self):
        """Test ReminderViewSet create"""
        # Create a location and group for the event
        location = Location.objects.create(
            street_address="123 Test St",
            city="Test City",
            country="SG",
            postalcode="12345"
        )
        
        group = Group.objects.create(
            name="Test Group",
            description="Test Description",
            creator=self.user1.profile
        )
        
        # Create an event for the user
        event = Event.objects.create(
            title="Test Event",
            creator=self.user1.profile,
            location_id=location,
            group=group
        )
        
        # Add user1 as participant to the event
        EventParticipant.objects.create(
            event=event,
            participant=self.user1.profile
        )
        
        # Create a calendar entry
        calendar_entry = CalendarEntry.objects.create(
            title="Test Calendar Entry",
            description="Test Description",
            start_date=date(2024, 1, 1),
            start_time=time(10, 0),
            end_date=date(2024, 1, 1),
            end_time=time(11, 0),
            duration=60,
            source="manual",
            user=self.user1.profile,
            event=event
        )
        
        url = reverse("reminder-list")
        data = {
            "remind_at": "2024-01-01T09:30:00Z",
            "calendar_entry": calendar_entry.id,
            "user": self.user1.profile.unique_id
        }
        
        response = self.client.post(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Reminder.objects.count(), 1)

    def test_reminder_viewset_other_user_reminders(self):
        """Test ReminderViewSet doesn't show other user's reminders"""
        # Create calendar entry for user2
        entry = CalendarEntry.objects.create(
            user=self.profile2,
            title="User2 Entry",
            start_date=date(2024, 1, 1),
            start_time=time(10, 0),
            end_date=date(2024, 1, 1),
            end_time=time(11, 0),
            source="manual"
        )
        
        # Create reminder for user2
        Reminder.objects.create(
            user_id=self.profile2,
            remind_at=datetime(2024, 1, 1, 10, 0, 0),
            calendar_entry_id=entry
        )

        url = reverse("reminder-list")
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)  # Should not see user2's reminders

    @patch('availcalendar.views.get_google_token')
    @patch('availcalendar.views.fetch_google_busy_slots')
    def test_google_calendar_sync_view_get_success(self, mock_fetch_busy, mock_get_token):
        """Test GoogleCalendarSyncView GET success"""
        mock_get_token.return_value = "test_token"
        mock_fetch_busy.return_value = (
            [
                {"start": "2024-01-01T10:00:00Z", "end": "2024-01-01T11:00:00Z"}
            ],
            None
        )

        url = reverse("calendar-google-sync")
        response = self.client.get(url, {
            "start": "2024-01-01T00:00:00Z",
            "end": "2024-01-01T23:59:59Z",
            "calendars": "primary"
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("busy", response.data)

    @patch('availcalendar.views.get_google_token')
    def test_google_calendar_sync_view_get_no_token(self, mock_get_token):
        """Test GoogleCalendarSyncView GET without token"""
        mock_get_token.return_value = None

        url = reverse("calendar-google-sync")
        response = self.client.get(url, {
            "start": "2024-01-01T00:00:00Z",
            "end": "2024-01-01T23:59:59Z",
            "calendars": "primary"
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    @patch('availcalendar.views.get_google_token')
    @patch('availcalendar.views.fetch_google_busy_slots')
    def test_google_calendar_sync_view_get_fetch_error(self, mock_fetch_busy, mock_get_token):
        """Test GoogleCalendarSyncView GET with fetch error"""
        mock_get_token.return_value = "test_token"
        mock_fetch_busy.return_value = (None, "API Error")

        url = reverse("calendar-google-sync")
        response = self.client.get(url, {
            "start": "2024-01-01T00:00:00Z",
            "end": "2024-01-01T23:59:59Z",
            "calendars": "primary"
        })
        
        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertIn("error", response.data)

    @patch('availcalendar.views.sync_google_calendar_task')
    @patch('availcalendar.views.get_google_token')
    def test_google_calendar_sync_view_put_success(self, mock_get_token, mock_sync_task):
        """Test GoogleCalendarSyncView PUT success"""
        mock_get_token.return_value = "test_token"
        mock_sync_task.return_value = {"status": "Success", "new_slots": 2}

        url = reverse("calendar-google-sync")
        response = self.client.put(url, {
            "start": "2024-01-01T00:00:00Z",
            "end": "2024-01-01T23:59:59Z",
            "calendars": ["primary"]
        }, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertIn("message", response.data)

    @patch('availcalendar.views.get_google_token')
    @patch('availcalendar.views.sync_google_calendar_task')
    def test_google_calendar_sync_view_put_no_token(self, mock_sync_task, mock_get_token):
        """Test GoogleCalendarSyncView PUT without token"""
        mock_get_token.return_value = None
        mock_sync_task.delay.return_value = None
        
        url = reverse("calendar-google-sync")
        response = self.client.put(url, {
            "start": "2024-01-01T00:00:00Z",
            "end": "2024-01-01T23:59:59Z",
            "calendars": ["primary"]
        }, format="json")
        
        # The view always returns 202 when the task is queued, regardless of token
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertIn("Calendar synchronization initiated", response.data["message"])

    @patch('availcalendar.views.sync_google_calendar_task')
    @patch('availcalendar.views.get_google_token')
    def test_google_calendar_sync_view_put_task_error(self, mock_get_token, mock_sync_task):
        """Test GoogleCalendarSyncView PUT with task error"""
        mock_get_token.return_value = "test_token"
        mock_sync_task.return_value = {"status": "Failed", "error": "Task Error"}

        url = reverse("calendar-google-sync")
        response = self.client.put(url, {
            "start": "2024-01-01T00:00:00Z",
            "end": "2024-01-01T23:59:59Z",
            "calendars": ["primary"]
        }, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertIn("message", response.data)

    def test_google_calendar_sync_view_unauthenticated(self):
        """Test GoogleCalendarSyncView without authentication"""
        self.client.logout()
        
        url = reverse("calendar-google-sync")
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_month_availability_view(self):
        """Test month availability view"""
        # Create some manual availabilities
        ManualAvailability.objects.create(
            user=self.profile1,
            start_date=date(2024, 1, 1),
            start_time=time(10, 0),
            end_date=date(2024, 1, 1),
            end_time=time(11, 0),
            duration=60
        )

        url = reverse("month-availability")
        response = self.client.get(url, {
            "year": "2024",
            "month": "1"
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # The response is a list of daily availability data
        self.assertIsInstance(response.data, list)
        self.assertTrue(len(response.data) > 0)

    def test_month_availability_view_invalid_params(self):
        """Test month availability view with invalid parameters"""
        url = reverse("month-availability")
        response = self.client.get(url, {
            "year": "invalid",
            "month": "invalid"
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_month_availability_view_unauthenticated(self):
        """Test month availability view without authentication"""
        self.client.logout()
        
        url = reverse("month-availability")
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
