from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, time, timedelta
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from polls.models import Poll, PollOption, PollVote
from events.models import Event, EventParticipant
from accounts.models import Profile, Location
from availcalendar.models import TimeSlot


class PollTestCase(APITestCase):
    """
    # Tests Poll Feature Functionalities
    """

    @patch("accounts.models.geolocator.geocode")
    def setUp(self, mock_geocode):
        # Mock geocode
        mock_location = MagicMock()
        mock_location.latitude = 1.3521
        mock_location.longitude = 103.8198
        mock_geocode.return_value = mock_location

        # Create test users
        self.user1 = User.objects.create_user(
            username="testuser1", password="testpass123", email="test1@gmail.com"
        )
        self.user2 = User.objects.create_user(
            username="testuser2", password="testpass123", email="test2@gmail.com"
        )
        self.user3 = User.objects.create_user(
            username="testuser3", password="testpass123", email="test3@gmail.com"
        )

        # Create test locations
        self.location = Location.objects.create(
            postalcode="117417",
            city="Singapore",
            country="SG",
            street_address="13 Computing Drive",
        )

        # Set up user profiles
        self.profile1 = Profile.objects.get(user=self.user1)
        self.profile2 = Profile.objects.get(user=self.user2)
        self.profile3 = Profile.objects.get(user=self.user3)

        # Set up API client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)

        # Create Event
        self.event = Event.objects.create(
            title="Test Event",
            description="A test event for polling",
            creator=self.profile1,
            location_id=self.location,
        )

        # Add participants to event
        EventParticipant.objects.create(
            event=self.event, participant=self.profile1, is_joining="going"
        )
        EventParticipant.objects.create(
            event=self.event, participant=self.profile2, is_joining="going"
        )
        EventParticipant.objects.create(
            event=self.event, participant=self.profile3, is_joining="maybe"
        )

        # Create test timeslots
        self.timeslot1 = TimeSlot.objects.create(
            event_id=self.event,
            start_date=date(2025, 6, 20),
            start_time=time(10, 0),
            end_date=date(2025, 6, 20),
            end_time=time(11, 0),
            duration=60,
            status="not confirmed",
        )
        self.timeslot2 = TimeSlot.objects.create(
            event_id=self.event,
            start_date=date(2025, 6, 21),
            start_time=time(14, 0),
            end_date=date(2025, 6, 21),
            end_time=time(15, 0),
            duration=60,
            status="not confirmed",
        )

        # Create Poll
        self.poll = Poll.objects.create(event=self.event)

        # Create Poll Options
        self.poll_option1 = PollOption.objects.create(
            poll=self.poll, timeslot=self.timeslot1
        )
        self.poll_option2 = PollOption.objects.create(
            poll=self.poll, timeslot=self.timeslot2
        )

    def test_create_poll_as_organiser(self):
        """
        Test that event organisers can create polls
        """
        url = reverse("poll-list")
        data = {
            "event": self.event.id,
            "option_ids": [self.timeslot1.id, self.timeslot2.id],
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["event"], self.event.id)
        self.assertEqual(len(response.data["options"]), 2)
        self.assertEqual(response.data["total_votes"], 0)

    def test_create_poll_as_non_organiser_fails(self):
        """
        Test that non-organisers cannot create polls
        """
        self.client.force_authenticate(user=self.user2)
        url = reverse("poll-list")
        data = {
            "event": self.event.id,
            "option_ids": [self.timeslot1.id, self.timeslot2.id],
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("Only event organisers can create a poll", str(response.data))

    def test_create_poll_with_invalid_timeslot_fails(self):
        """
        Test that creating a poll with timeslots from different events fails
        """
        # Create another event and timeslot
        other_event = Event.objects.create(
            title="Other Event",
            description="Another test event",
            creator=self.profile2,
            location_id=self.location,
        )
        other_timeslot = TimeSlot.objects.create(
            event_id=other_event,
            start_date=date(2025, 6, 22),
            start_time=time(16, 0),
            end_date=date(2025, 6, 22),
            end_time=time(17, 0),
            duration=60,
            status="not confirmed",
        )

        url = reverse("poll-list")
        data = {
            "event": self.event.id,
            "option_ids": [self.timeslot1.id, other_timeslot.id],
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("does not belong to Event", str(response.data))

    def test_list_polls(self):
        """
        Test listing all polls
        """
        url = reverse("poll-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertTrue(any(poll["id"] == self.poll.id for poll in response.data))

    def test_retrieve_poll(self):
        """
        Test retrieving a specific poll with options and vote counts
        """
        url = reverse("poll-detail", kwargs={"pk": self.poll.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.poll.id)
        self.assertEqual(response.data["event"], self.event.id)
        self.assertEqual(len(response.data["options"]), 2)
        self.assertEqual(response.data["total_votes"], 0)

    def test_delete_poll_as_organiser(self):
        """
        Test that organisers can delete polls
        """
        url = reverse("poll-detail", kwargs={"pk": self.poll.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Poll.objects.filter(id=self.poll.id).exists())

    def test_delete_poll_as_non_organiser_fails(self):
        """
        Test that non-organisers cannot delete polls
        """
        self.client.force_authenticate(user=self.user2)
        url = reverse("poll-detail", kwargs={"pk": self.poll.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("Only organisers can delete the poll", response.data["error"])
        self.assertTrue(Poll.objects.filter(id=self.poll.id).exists())

    @patch("polls.views.schedule_best_timeslots")
    def test_generate_poll_as_organiser(self, mock_schedule):
        """
        Test that organisers can generate polls using smart scheduling
        """
        # Mock the scheduling engine response
        mock_schedule.return_value = [
            {
                "start_date": date(2025, 6, 20),
                "start_time": time(10, 0),
                "end_date": date(2025, 6, 20),
                "end_time": time(11, 0),
                "duration": 60,
            },
            {
                "start_date": date(2025, 6, 21),
                "start_time": time(14, 0),
                "end_date": date(2025, 6, 21),
                "end_time": time(15, 0),
                "duration": 60,
            },
        ]

        url = reverse("poll-generate-poll")
        data = {
            "event": self.event.id,
            "start_date": "2025-06-20",
            "start_time": "09:00:00",
            "end_date": "2025-06-25",
            "end_time": "17:00:00",
            "duration": 60,
            "buffer": 15,
            "min_attendance": 0.5,
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["event"], self.event.id)
        self.assertEqual(len(response.data["options"]), 2)
        self.assertEqual(response.data["total_votes"], 0)

    @patch("polls.views.schedule_best_timeslots")
    def test_generate_poll_as_non_organiser_fails(self, mock_schedule):
        """
        Test that non-organisers cannot generate polls
        """
        self.client.force_authenticate(user=self.user2)
        url = reverse("poll-generate-poll")
        data = {
            "event": self.event.id,
            "start_date": "2025-06-20",
            "start_time": "09:00:00",
            "end_date": "2025-06-25",
            "end_time": "17:00:00",
            "duration": 60,
            "buffer": 15,
            "min_attendance": 0.5,
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("Only organisers can generate a poll", response.data["error"])

    @patch("polls.views.schedule_best_timeslots")
    def test_generate_poll_no_suitable_timeslots(self, mock_schedule):
        """
        Test generating poll when no suitable timeslots are found
        """
        mock_schedule.return_value = []

        url = reverse("poll-generate-poll")
        data = {
            "event": self.event.id,
            "start_date": "2025-06-20",
            "start_time": "09:00:00",
            "end_date": "2025-06-25",
            "end_time": "17:00:00",
            "duration": 60,
            "buffer": 15,
            "min_attendance": 0.5,
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIn("No timeslots fit the criteria", response.data["error"])

    def test_list_poll_options(self):
        """
        Test listing poll options with vote counts
        """
        url = reverse("poll-list-options", kwargs={"pk": self.poll.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["vote_count"], 0)
        self.assertEqual(response.data[1]["vote_count"], 0)

    def test_delete_poll_option_as_organiser(self):
        """
        Test that organisers can delete poll options
        """
        url = reverse("poll-option-detail", kwargs={"pk": self.poll_option1.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(PollOption.objects.filter(id=self.poll_option1.id).exists())

    def test_delete_poll_option_as_non_organiser_fails(self):
        """
        Test that non-organisers cannot delete poll options
        """
        self.client.force_authenticate(user=self.user2)
        url = reverse("poll-option-detail", kwargs={"pk": self.poll_option1.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("Only organisers can delete poll options", response.data["error"])
        self.assertTrue(PollOption.objects.filter(id=self.poll_option1.id).exists())

    def test_cast_vote_as_participant(self):
        """
        Test that event participants can cast votes
        """
        self.client.force_authenticate(user=self.user2)
        url = reverse("poll-vote-list")
        data = {"poll_option": self.poll_option1.id}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["poll_option"], self.poll_option1.id)
        self.assertEqual(response.data["voter"]["user"], self.user2.username)
        self.assertTrue(PollVote.objects.filter(poll_option=self.poll_option1, voter=self.profile2).exists())

    def test_cast_vote_as_non_participant_fails(self):
        """
        Test that non-participants cannot cast votes
        """
        # Create a user who is not a participant
        user4 = User.objects.create_user(
            username="testuser4", password="testpass123", email="test4@gmail.com"
        )
        self.client.force_authenticate(user=user4)
        
        url = reverse("poll-vote-list")
        data = {"poll_option": self.poll_option1.id}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("You are not a participant of this event", str(response.data))

    def test_cast_duplicate_vote_fails(self):
        """
        Test that users cannot vote for the same option twice
        """
        # First vote
        self.client.force_authenticate(user=self.user2)
        url = reverse("poll-vote-list")
        data = {"poll_option": self.poll_option1.id}
        self.client.post(url, data, format="json")

        # Second vote for same option
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("You have already voted for this option", str(response.data))

    def test_cast_vote_for_different_options(self):
        """
        Test that users can vote for different options
        """
        self.client.force_authenticate(user=self.user2)
        url = reverse("poll-vote-list")
        
        # Vote for first option
        data1 = {"poll_option": self.poll_option1.id}
        response1 = self.client.post(url, data1, format="json")
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        # Vote for second option
        data2 = {"poll_option": self.poll_option2.id}
        response2 = self.client.post(url, data2, format="json")
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)

        # Check that both votes exist
        self.assertTrue(PollVote.objects.filter(poll_option=self.poll_option1, voter=self.profile2).exists())
        self.assertTrue(PollVote.objects.filter(poll_option=self.poll_option2, voter=self.profile2).exists())

    def test_revoke_own_vote(self):
        """
        Test that users can revoke their own votes
        """
        # Create a vote
        vote = PollVote.objects.create(
            poll_option=self.poll_option1, voter=self.profile2
        )

        self.client.force_authenticate(user=self.user2)
        url = reverse("poll-vote-detail", kwargs={"pk": vote.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(PollVote.objects.filter(id=vote.id).exists())

    def test_revoke_others_vote_fails(self):
        """
        Test that users cannot revoke others' votes
        """
        # Create a vote for user2
        vote = PollVote.objects.create(
            poll_option=self.poll_option1, voter=self.profile2
        )

        # Try to revoke as user3
        self.client.force_authenticate(user=self.user3)
        url = reverse("poll-vote-detail", kwargs={"pk": vote.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("You can only revoke your own vote", response.data["error"])
        self.assertTrue(PollVote.objects.filter(id=vote.id).exists())

    def test_vote_count_updates_correctly(self):
        """
        Test that vote counts update correctly when votes are cast and revoked
        """
        # Cast votes
        PollVote.objects.create(poll_option=self.poll_option1, voter=self.profile1)
        PollVote.objects.create(poll_option=self.poll_option1, voter=self.profile2)
        PollVote.objects.create(poll_option=self.poll_option2, voter=self.profile3)

        # Check vote counts
        url = reverse("poll-list-options", kwargs={"pk": self.poll.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        option1_votes = next(opt["vote_count"] for opt in response.data if opt["id"] == self.poll_option1.id)
        option2_votes = next(opt["vote_count"] for opt in response.data if opt["id"] == self.poll_option2.id)
        
        self.assertEqual(option1_votes, 2)
        self.assertEqual(option2_votes, 1)

        # Check total votes in poll
        url = reverse("poll-detail", kwargs={"pk": self.poll.pk})
        response = self.client.get(url)
        self.assertEqual(response.data["total_votes"], 3)

    def test_poll_with_no_votes(self):
        """
        Test poll with no votes shows correct counts
        """
        url = reverse("poll-detail", kwargs={"pk": self.poll.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_votes"], 0)
        for option in response.data["options"]:
            self.assertEqual(option["vote_count"], 0)

    def test_poll_serializer_validation(self):
        """
        Test poll serializer validation
        """
        url = reverse("poll-list")
        
        # Test missing required fields
        data = {"event": self.event.id}  # Missing option_ids
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test empty option_ids
        data = {"event": self.event.id, "option_ids": []}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_poll_generate_serializer_validation(self):
        """
        Test poll generate serializer validation
        """
        url = reverse("poll-generate-poll")
        
        # Test missing required fields
        data = {"event": self.event.id}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test invalid duration
        data = {
            "event": self.event.id,
            "start_date": "2025-06-20",
            "start_time": "09:00:00",
            "end_date": "2025-06-25",
            "end_time": "17:00:00",
            "duration": 10,  # Less than minimum 15
            "buffer": 15,
            "min_attendance": 0.5,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test invalid min_attendance
        data = {
            "event": self.event.id,
            "start_date": "2025-06-20",
            "start_time": "09:00:00",
            "end_date": "2025-06-25",
            "end_time": "17:00:00",
            "duration": 60,
            "buffer": 15,
            "min_attendance": 1.5,  # Greater than maximum 1.0
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_event_with_no_participants_generate_fails(self):
        """
        Test that generating poll for event with no participants fails
        """
        # Create event with no participants
        empty_event = Event.objects.create(
            title="Empty Event",
            description="Event with no participants",
            creator=self.profile1,
            location_id=self.location,
        )

        url = reverse("poll-generate-poll")
        data = {
            "event": empty_event.id,
            "start_date": "2025-06-20",
            "start_time": "09:00:00",
            "end_date": "2025-06-25",
            "end_time": "17:00:00",
            "duration": 60,
            "buffer": 15,
            "min_attendance": 0.5,
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Event has no participants", str(response.data))
