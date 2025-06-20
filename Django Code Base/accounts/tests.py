from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Profile
from django.utils import timezone
from datetime import timedelta

class AccountTestCase(TestCase):
    """
    Test suite for the accounts app functionality
    """
    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(username = 'testuser1', password = 'testpass123')
        self.user2 = User.objects.create_user(username = 'testuser2', password = 'testpass123')
        
        # Get their profiles (auto-created by signal)
        self.profile1 = Profile.objects.get(user=self.user1)
        self.profile2 = Profile.objects.get(user=self.user2)
        
        # Set up API client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)

    def test_profile_creation(self):
        """
        Test that a profile is automatically created when a user is created
        """
        # Profile should be created automatically via signal
        self.assertIsNotNone(self.profile1)
        self.assertIsNotNone(self.profile1.unique_id)
        self.assertEqual(len(self.profile1.unique_id), 8)
        self.assertEqual(self.profile1.user, self.user1)

    def test_profile_update(self):
        """
        Test updating profile information
        """
        # Update profile information
        self.profile1.name = "Test User"
        self.profile1.location = "Test Location"
        self.profile1.save()

        # Verify updates
        updated_profile = Profile.objects.get(user=self.user1)
        self.assertEqual(updated_profile.name, "Test User")
        self.assertEqual(updated_profile.location, "Test Location")

    def test_unique_id_generation(self):
        """
        Test that unique IDs are actually unique
        """
        # Create multiple users and check their unique IDs
        unique_ids = set()
        for i in range(5):
            user = User.objects.create_user(username=f'testuser{i+3}', password='testpass123')
            profile = Profile.objects.get(user=user)
            unique_ids.add(profile.unique_id)
        
        # All IDs should be unique
        self.assertEqual(len(unique_ids), 5)

    def test_profile_str_representation(self):
        """
        Test the string representation of Profile model
        """
        expected_str = f"{self.user1.username}'s profile"
        self.assertEqual(str(self.profile1), expected_str)

    def test_profile_unique_constraints(self):
        """
        Test that profile unique_id remains unique
        """
        # Try to create a profile with a duplicate unique_id
        with self.assertRaises(Exception):
            Profile.objects.create(
                user=self.user2,
                unique_id=self.profile1.unique_id
            )

    def test_authentication_required(self):
        """
        Test that authentication is required for protected endpoints
        """
        # Create unauthenticated client
        client = APIClient()
        response = client.get('/api/profile/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_blank_fields(self):
        """
        Test that profile fields can be blank
        """
        # Create user without name or location
        user = User.objects.create_user(username='blankuser', password='testpass123')
        profile = Profile.objects.get(user=user)
        
        # Fields should be blank but not None
        self.assertEqual(profile.name, '')
        self.assertEqual(profile.location, '')
        self.assertIsNotNone(profile.unique_id)
