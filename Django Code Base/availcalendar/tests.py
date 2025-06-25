from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from availcalendar.models import Event, TimeSlot, CalendarEntry, ManualAvailability, Reminder, EventParticipant
from accounts.models import Profile, Location
from datetime import datetime, timedelta, date, time
from unittest.mock import patch, MagicMock

class BaseCalendarTestCase(APITestCase):
    """
    Test Cases for Event model
    """
    @patch('accounts.models.geolocator.geocode')
    def setUp(self, mock_geocode):
        # Mock geocode
        mock_location = MagicMock()
        mock_location.latitude = 1.3521
        mock_location.longitude = 103.8198
        mock_geocode.return_value = mock_location
        # Create a location
        self.location = Location.objects.create(
            postalcode = "117417",
            city = "Singapore",
            country = "SG",
            street_address = "13 Computing Drive"
        )
        # Create users and profiles
        self.user1 = User.objects.create_user(username='user1', password='pass123')
        self.user2 = User.objects.create_user(username='user2', password='pass123')
        self.profile1 = self.user1.profile
        self.profile1.name = "Test User 1"
        self.profile1.save()
        self.profile2 = self.user2.profile
        self.profile2.name = "Test User 2"
        self.profile2.save()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)

class EventTestCase(BaseCalendarTestCase):
    def setUp(self):
        super().setUp()
        self.event_url = reverse('event-list')

    def test_create_event(self):
        data = {
            "title": "Test Event",
            "description": "A test event.",
            "creator": self.profile1.pk,
            "location": self.location.pk,
            "participants_to_add": [self.profile2.pk],
        }
        response = self.client.post(self.event_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], "Test Event")
        
        # Check that both creator (profile1) and the added participant (profile2) are in the event
        participant_ids = [p['participant_id'] for p in response.data['participants']]
        self.assertIn(self.profile1.pk, participant_ids)
        self.assertIn(self.profile2.pk, participant_ids)

    def test_event_list_only_own(self):
        event = Event.objects.create(title="E1", description="", creator=self.profile1, location_id=self.location)
        EventParticipant.objects.create(event=event, participant=self.profile1)
        response = self.client.get(self.event_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(e['id'] == event.id for e in response.data))

    def test_event_delete_permission(self):
        event = Event.objects.create(title="E2", description="", creator=self.profile1, location_id=self.location)
        EventParticipant.objects.create(event=event, participant=self.profile2)
        url = reverse('event-detail', kwargs={'pk': event.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Try as another user
        self.client.force_authenticate(user=self.user2)
        event2 = Event.objects.create(title="E3", description="", creator=self.profile1, location_id=self.location)
        EventParticipant.objects.create(event=event2, participant=self.profile2)
        url2 = reverse('event-detail', kwargs={'pk': event2.pk})
        response2 = self.client.delete(url2)
        self.assertEqual(response2.status_code, status.HTTP_403_FORBIDDEN)

class TimeSlotTestCase(BaseCalendarTestCase):
    def setUp(self):
        super().setUp()
        self.event = Event.objects.create(title="Event", description="", creator=self.profile1, location_id=self.location)
        EventParticipant.objects.create(event=self.event, participant=self.profile1)
        self.timeslot_url = reverse('timeslot-list')

    def test_create_valid_timeslot(self):
        data = {
            "event": self.event.pk,
            "user": self.profile1.pk,
            "start_date": "2024-01-01",
            "start_time": "10:00",
            "end_date": "2024-01-01",
            "end_time": "10:15",
            "duration": 15,
            "status": "not confirmed"
        }
        response = self.client.post(self.timeslot_url, data, format='json')
        # print("RESPONSE DATA:", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invalid_timeslot_interval(self):
        start = datetime.now().replace(minute=0, second=0, microsecond=0)
        end = start + timedelta(minutes=10)
        data = {
            "event": self.event.pk,
            "user": self.profile1.pk,
            "start_date": start.date().isoformat(),
            "start_time": start.time().isoformat(timespec='minutes'),
            "end_date": end.date().isoformat(),
            "end_time": end.time().isoformat(timespec='minutes'),
            "duration": 10,
            "status": "not confirmed"
        }
        response = self.client.post(self.timeslot_url, data, format='json')
        # print("RESPONSE DATA:", response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invalid_timeslot_boundary(self):
        start = datetime.now().replace(minute=7, second=0, microsecond=0)
        end = start + timedelta(minutes=15)
        data = {
            "event": self.event.pk,
            "user": self.profile1.pk,
            "start_date": start.date().isoformat(),
            "start_time": start.time().isoformat(timespec='minutes'),
            "end_date": end.date().isoformat(),
            "end_time": end.time().isoformat(timespec='minutes'),
            "duration": 15,
            "status": "not confirmed"
        }
        response = self.client.post(self.timeslot_url, data, format='json')
        # print("RESPONSE DATA:", response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class CalendarEntryTestCase(BaseCalendarTestCase):
    def setUp(self):
        super().setUp()
        self.event = Event.objects.create(title="Event", description="", creator=self.profile1, location_id=self.location)
        EventParticipant.objects.create(event=self.event, participant=self.profile1)
        self.calendar_url = reverse('calendar-entry-list')

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
            "event": self.event.pk
        }
        response = self.client.post(self.calendar_url, data, format='json')
        # print("RESPONSE DATA:", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], "Meeting")

    def test_create_invalid_calendar_entry_short(self):
        start = datetime.now().replace(minute=0, second=0, microsecond=0)
        end = start + timedelta(minutes=10)
        data = {
            "title": "Short Meeting",
            "description": "Too short",
            "start_date": start.date().isoformat(),
            "start_time": start.time().isoformat(timespec='minutes'),
            "end_date": end.date().isoformat(),
            "end_time": end.time().isoformat(timespec='minutes'),
            "duration": 10,
            "source": "manual",
            "location": self.location.pk,
            "user": self.profile1.pk,
            "event": self.event.pk
        }
        response = self.client.post(self.calendar_url, data, format='json')
        # print("RESPONSE DATA:", response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invalid_calendar_entry_start_after_end(self):
        start = datetime.now().replace(minute=0, second=0, microsecond=0)
        end = start - timedelta(minutes=15)
        data = {
            "title": "Backwards Meeting",
            "description": "Start after end",
            "start_date": start.date().isoformat(),
            "start_time": start.time().isoformat(timespec='minutes'),
            "end_date": end.date().isoformat(),
            "end_time": end.time().isoformat(timespec='minutes'),
            "duration": -15,
            "source": "manual",
            "location": self.location.pk,
            "user": self.profile1.pk,
            "event": self.event.pk
        }
        response = self.client.post(self.calendar_url, data, format='json')
        # print("RESPONSE DATA:", response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class ManualAvailabilityTestCase(BaseCalendarTestCase):
    def setUp(self):
        super().setUp()
        self.manual_url = reverse('manual-availability-list')

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
            "count": 2
        }
        response = self.client.post(self.manual_url, data, format='json')
        # print("RESPONSE DATA:", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("recurrence", response.data)

    def test_create_manual_availability_invalid_interval(self):
        start = datetime.now().replace(minute=0, second=0, microsecond=0)
        end = start + timedelta(minutes=10)
        data = {
            "start_date": start.date().isoformat(),
            "start_time": start.time().isoformat(timespec='minutes'),
            "end_date": end.date().isoformat(),
            "end_time": end.time().isoformat(timespec='minutes'),
            "duration": 10,
            "freq": "DAILY",
            "interval": 1
        }
        response = self.client.post(self.manual_url, data, format='json')
        # print("RESPONSE DATA:", response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_availability_start_after_end(self):
        start = datetime.now().replace(minute=0, second=0, microsecond=0)
        end = start - timedelta(minutes=15)
        data = {
            "start_date": start.date().isoformat(),
            "start_time": start.time().isoformat(timespec='minutes'),
            "end_date": end.date().isoformat(),
            "end_time": end.time().isoformat(timespec='minutes'),
            "duration": -15,
            "freq": "DAILY",
            "interval": 1
        }
        response = self.client.post(self.manual_url, data, format='json')
        # print("RESPONSE DATA:", response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class ReminderTestCase(BaseCalendarTestCase):
    def setUp(self):
        super().setUp()
        self.event = Event.objects.create(title="Event", description="", creator=self.profile1, location_id=self.location)
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
            location_id=self.location,
            user_id=self.profile1,
            event_id=self.event
        )
        self.reminder_url = reverse('reminder-list')

    def test_create_reminder(self):
        remind_at = datetime.now() + timedelta(minutes=5)
        data = {
            "remind_at": remind_at.isoformat(),
            "calendar_entry": self.calendar_entry.pk,
            "user": self.profile1.pk
        }
        response = self.client.post(self.reminder_url, data, format='json')
        # print("RESPONSE DATA:", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_reminder_exclusive_to_user(self):
        remind_at = datetime.now() + timedelta(minutes=5)
        data = {
            "remind_at": remind_at.isoformat(),
            "calendar_entry": self.calendar_entry.pk,
            "user": self.profile1.pk
        }
        self.client.post(self.reminder_url, data, format='json')
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(self.reminder_url)
        # print("RESPONSE DATA:", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)