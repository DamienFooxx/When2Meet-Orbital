from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from events.models import Event, EventParticipant
from accounts.models import Profile, Location
from unittest.mock import patch, MagicMock

class BaseEventsTestCase(APITestCase):
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


class EventTestCase(BaseEventsTestCase):
    def setUp(self):
        super().setUp()
        self.event_url = reverse("event-list")

    def test_create_event(self):
        data = {
            "title": "Test Event",
            "description": "A test event.",
            "creator": self.profile1.pk,
            "location": self.location.pk,
            "participants_to_add": [self.profile2.pk],
        }
        response = self.client.post(self.event_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Test Event")

        # Check that both creator (profile1) and the added participant (profile2) are in the event
        participant_ids = [p["participant_id"] for p in response.data["participants"]]
        self.assertIn(self.profile1.pk, participant_ids)
        self.assertIn(self.profile2.pk, participant_ids)

    def test_event_list_only_own(self):
        event = Event.objects.create(
            title="E1", description="", creator=self.profile1, location_id=self.location
        )
        EventParticipant.objects.create(event=event, participant=self.profile1)
        response = self.client.get(self.event_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(e["id"] == event.id for e in response.data))

    def test_event_delete_permission(self):
        event = Event.objects.create(
            title="E2", description="", creator=self.profile1, location_id=self.location
        )
        EventParticipant.objects.create(event=event, participant=self.profile2)
        url = reverse("event-detail", kwargs={"pk": event.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Try as another user
        self.client.force_authenticate(user=self.user2)
        event2 = Event.objects.create(
            title="E3", description="", creator=self.profile1, location_id=self.location
        )
        EventParticipant.objects.create(event=event2, participant=self.profile2)
        url2 = reverse("event-detail", kwargs={"pk": event2.pk})
        response2 = self.client.delete(url2)
        self.assertEqual(response2.status_code, status.HTTP_403_FORBIDDEN)
