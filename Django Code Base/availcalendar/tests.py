from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.modes import User
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from availcalendar.models import Event, TimeSlot, CalendarEntry, ManualAvailability, Reminder
from accounts.models import Profile, Location
from datetime import datetime, timedelta

class BaseCalendarTestCase(APITestCase):
    """
    Test Cases for Event model
    """
    def setUp(self):
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
        self.profile1 = Profile.objects.create(user=self.user1, name="User One", location=self.location)
        self.profile2 = Profile.objects.create(user=self.user2, name="User Two", location=self.location)
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
            "participants": [self.profile1.pk, self.profile2.pk],
        }
        response = self.client.post(self.event_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], "Test Event")
        self.assertIn(self.profile2.pk, response.data['participants'])

    def test_event_list_only_own(self):
        event = Event.objects.create(title="E1", description="", creator=self.profile1, location_id=self.location)
        event.participants.add(self.profile1)
        response = self.client.get(self.event_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(e['id'] == event.id for e in response.data))

    def test_event_delete_permission(self):
        event = Event.objects.create(title="E2", description="", creator=self.profile1, location_id=self.location)
        url = reverse('event-detail', kwargs={'pk': event.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Try as another user
        self.client.force_authenticate(user=self.user2)
        event2 = Event.objects.create(title="E3", description="", creator=self.profile1, location_id=self.location)
        url2 = reverse('event-detail', kwargs={'pk': event2.pk})
        response2 = self.client.delete(url2)
        self.assertEqual(response2.status_code, status.HTTP_403_FORBIDDEN)

class TimeSlotTestCase(BaseCalendarTestCase):
    def setUp(self):
        super().setUp()
        self.event = Event.objects.create(title="Event", description="", creator=self.profile1, location_id=self.location)
        self.event.participants.add(self.profile1)
        self.timeslot_url = reverse('timeslot-list')

    def test_create_valid_timeslot(self):
        start = datetime.now().replace(minute=0, second=0, microsecond=0)
        end = start + timedelta(minutes=15)
        data = {
            "event": self.event.pk,
            "user": self.profile1.pk,
            "start": start.isoformat(),
            "end": end.isoformat(),
            "status": "not confirmed"
        }
        response = self.client.post(self.timeslot_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invalid_timeslot_interval(self):
        start = datetime.now().replace(minute=0, second=0, microsecond=0)
        end = start + timedelta(minutes=10)
        data = {
            "event": self.event.pk,
            "user": self.profile1.pk,
            "start": start.isoformat(),
            "end": end.isoformat(),
            "status": "not confirmed"
        }
        response = self.client.post(self.timeslot_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invalid_timeslot_boundary(self):
        start = datetime.now().replace(minute=7, second=0, microsecond=0)
        end = start + timedelta(minutes=15)
        data = {
            "event": self.event.pk,
            "user": self.profile1.pk,
            "start": start.isoformat(),
            "end": end.isoformat(),
            "status": "not confirmed"
        }
        response = self.client.post(self.timeslot_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class CalendarEntryTestCase(BaseCalendarTestCase):
    def setUp(self):
        super().setUp()
        self.event = Event.objects.create(title="Event", description="", creator=self.profile1, location_id=self.location)
        self.event.participants.add(self.profile1)
        self.calendar_url = reverse('calendar-entry-list')

    def test_create_valid_calendar_entry(self):
        start = datetime.now().replace(minute=0, second=0, microsecond=0)
        end = start + timedelta(minutes=15)
        data = {
            "title": "Meeting",
            "description": "Discuss project",
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
            "source": "manual",
            "location": self.location.pk,
            "user": self.profile1.pk,
            "event": self.event.pk
        }
        response = self.client.post(self.calendar_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], "Meeting")

    def test_create_invalid_calendar_entry_short(self):
        start = datetime.now().replace(minute=0, second=0, microsecond=0)
        end = start + timedelta(minutes=10)
        data = {
            "title": "Short Meeting",
            "description": "Too short",
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
            "source": "manual",
            "location": self.location.pk,
            "user": self.profile1.pk,
            "event": self.event.pk
        }
        response = self.client.post(self.calendar_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invalid_calendar_entry_start_after_end(self):
        start = datetime.now().replace(minute=0, second=0, microsecond=0)
        end = start - timedelta(minutes=15)
        data = {
            "title": "Backwards Meeting",
            "description": "Start after end",
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
            "source": "manual",
            "location": self.location.pk,
            "user": self.profile1.pk,
            "event": self.event.pk
        }
        response = self.client.post(self.calendar_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class ManualAvailabilityTestCase(BaseCalendarTestCase):
    def setUp(self):
        super().setUp()
        self.manual_url = reverse('manual-availability-list')

    def test_create_manual_availability_valid(self):
        start = datetime.now().replace(minute=0, second=0, microsecond=0)
        end = start + timedelta(minutes=30)
        data = {
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
            "freq": "DAILY",
            "interval": 1,
            "by_day": ["MO", "WE"],
            "count": 2
        }
        response = self.client.post(self.manual_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("recurrence", response.data)

    def test_create_manual_availability_invalid_interval(self):
        start = datetime.now().replace(minute=0, second=0, microsecond=0)
        end = start + timedelta(minutes=10)
        data = {
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
            "freq": "DAILY",
            "interval": 1
        }
        response = self.client.post(self.manual_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_manual_availability_start_after_end(self):
        start = datetime.now().replace(minute=0, second=0, microsecond=0)
        end = start - timedelta(minutes=15)
        data = {
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
            "freq": "DAILY",
            "interval": 1
        }
        response = self.client.post(self.manual_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class ReminderTestCase(BaseCalendarTestCase):
    def setUp(self):
        super().setUp()
        self.event = Event.objects.create(title="Event", description="", creator=self.profile1, location_id=self.location)
        self.event.participants.add(self.profile1)
        self.calendar_entry = CalendarEntry.objects.create(
            title="Meeting",
            description="Discuss project",
            start_time=datetime.now().replace(minute=0, second=0, microsecond=0),
            end_time=datetime.now().replace(minute=0, second=0, microsecond=0) + timedelta(minutes=15),
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
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)