from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from accounts.models import Profile, Location
from availcalendar.models import CalendarEntry, ManualAvailability
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta, date, time

class BaseSmartSchedulingTestCase(APITestCase):
    """
    Base setup for Smart Scheduling tests
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
        self.profile2 = self.user2.profile
        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)
        self.url = reverse("smartschedule-find-available-slots")

class SmartSchedulingTestCase(BaseSmartSchedulingTestCase):
    def setUp(self):
        super().setUp()
        # Add a busy slot for user2 to test busy logic
        CalendarEntry.objects.create(
            title="Busy Meeting",
            description="",
            start_date=date(2024, 1, 1),
            start_time=time(10, 0),
            end_date=date(2024, 1, 1),
            end_time=time(10, 30),
            duration=30,
            source="manual",
            location=self.location,
            user=self.profile2,
            event_id=None,
        )

    def test_find_available_slots_valid(self):
        data = {
            "users": [self.profile1.unique_id, self.profile2.unique_id],
            "start_date": "2024-01-01",
            "end_date": "2024-01-01",
            "start_time": "10:00",
            "end_time": "11:00",
            "duration": 30,
            "type_of_meetup": "virtual",
            "minimum_attendance": 0.0
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("available_slots", response.data)
        # At least one slot should be available for user1 (user2 is busy at 10:00-10:30)
        slots = response.data["available_slots"]
        self.assertTrue(any(slot["free_count"] >= 1 for slot in slots))

    def test_missing_required_field(self):
        data = {
            # Missing 'users'
            "start_date": "2024-01-01",
            "end_date": "2024-01-01",
            "start_time": "10:00",
            "end_time": "11:00",
            "duration": 30,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("users", response.data)

    def test_invalid_duration_not_multiple_of_15(self):
        data = {
            "users": [self.profile1.unique_id],
            "start_date": "2024-01-01",
            "end_date": "2024-01-01",
            "start_time": "10:00",
            "end_time": "11:00",
            "duration": 17,  # Not a multiple of 15
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("duration", response.data)

    def test_invalid_buffer_not_multiple_of_15(self):
        data = {
            "users": [self.profile1.unique_id],
            "start_date": "2024-01-01",
            "end_date": "2024-01-01",
            "start_time": "10:00",
            "end_time": "11:00",
            "duration": 30,
            "buffer": 7,  # Not a multiple of 15
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("buffer", response.data)

    def test_user_not_found(self):
        data = {
            "users": ["notarealuser"],
            "start_date": "2024-01-01",
            "end_date": "2024-01-01",
            "start_time": "10:00",
            "end_time": "11:00",
            "duration": 30,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertIn("Users not found", response.data["error"])

    def test_negative_buffer(self):
        data = {
            "users": [self.profile1.unique_id],
            "start_date": "2024-01-01",
            "end_date": "2024-01-01",
            "start_time": "10:00",
            "end_time": "11:00",
            "duration": 30,
            "buffer": -15,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("buffer", response.data)

    def test_zero_duration(self):
        data = {
            "users": [self.profile1.unique_id],
            "start_date": "2024-01-01",
            "end_date": "2024-01-01",
            "start_time": "10:00",
            "end_time": "11:00",
            "duration": 0,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("duration", response.data)

    def test_minimum_attendance_filter(self):
        # Only user1 is free, set minimum_attendance to 100%
        data = {
            "users": [self.profile1.unique_id, self.profile2.unique_id],
            "start_date": "2024-01-01",
            "end_date": "2024-01-01",
            "start_time": "10:00",
            "end_time": "11:00",
            "duration": 30,
            "minimum_attendance": 100.0
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # No slot should have 100% attendance since user2 is busy
        slots = response.data["available_slots"]
        self.assertTrue(all(slot["attendance"] == 100 for slot in slots)) 