from django.test import TestCase
from django.contrib.auth.models import User
from .models import Event, TimeSlot
from datetime import datetime, timedelta
from django.utils import timezone

# Create your tests here.

class EventModelTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_create_event(self):
        # Create an event
        event = Event.objects.create(
            title="Test Event",
            description="This is a test event",
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=1),
            creator=self.user
        )

        # Verify the event was created
        self.assertIsNotNone(event.id)
        self.assertEqual(event.title, "Test Event")
        self.assertEqual(event.creator, self.user)

    def test_create_time_slot(self):
        # Create an event first
        event = Event.objects.create(
            title="Test Event",
            description="This is a test event",
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=1),
            creator=self.user
        )

        # Create a time slot
        time_slot = TimeSlot.objects.create(
            event=event,
            user=self.user,
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=1)
        )

        # Verify the time slot was created
        self.assertIsNotNone(time_slot.id)
        self.assertEqual(time_slot.event, event)
        self.assertEqual(time_slot.user, self.user)
