from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from accounts.models import Profile, Location
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch, MagicMock

class LocationTestCase(APITestCase):
    """
    Test suite for location authentication
    """
    @patch('accounts.models.geolocator.geocode')
    def test_valid_location_save_coordinates(self, mock_geocode):
        mock_location = MagicMock()
        mock_location.latitude = 1.3521
        mock_location.longitude = 103.8198
        mock_geocode.return_value = mock_location

        loc = Location(
            postalcode = "117417",
            city = "Singapore",
            country = "SG",
            street_address = "13 Computing Drive"
        )
        loc.save()

        self.assertIsNotNone(loc.latitude)
        self.assertIsNotNone(loc.longitude)

    @patch('accounts.models.geolocator.geocode')
    def test_invalid_location_save_coordinates(self, mock_geocode):
        mock_geocode.return_value = None

        loc = Location(
            postalcode = "000000",
            city = "Nowhere",
            country = "SG",
            street_address = "Empty Street"
        )

        with self.assertRaises(ValidationError):
            loc.save()
    
    @patch('accounts.models.geolocator.geocode')
    def test_location_str_representation(self, mock_geocode):
        """
        Test the __str__ method of Location model returns the correct value
        """
        # Mock geocode
        mock_location = MagicMock()
        mock_location.latitude = 1.3521
        mock_location.longitude = 103.8198
        mock_geocode.return_value = mock_location
        # Case 1: postalcode is set
        loc1 = Location.objects.create(
            postalcode = "117417",
            city = "Singapore",
            country = "SG",
            street_address = "13 Computing Drive"
        )
        self.assertEqual(str(loc1), "117417")

        # Case 2: postalcode is blank, fallback to street_address
        loc2 = Location.objects.create(
            postalcode = "",
            city = "Singapore",
            street_address = "6 College Avenue East"
        )
        self.assertEqual(str(loc2), "6 College Avenue East")


class AccountTestCase(APITestCase):
    """
    Test suite for the accounts app functionality
    """
    def setUp(self):
        # Mock geocode
        self.mock_geocode = patch('accounts.models.geolocator.geocode').start()
        mock_location = MagicMock()
        mock_location.latitude = 1.3521
        mock_location.longitude = 103.8198
        self.mock_geocode.return_value = mock_location

        # Create test users
        self.user1 = User.objects.create_user(
            username = 'testuser1', 
            email = 'test1@gmail.com',
            password = 'testpass123',
            )
        self.user2 = User.objects.create_user(
            username = 'testuser2', 
            email = 'test2@gmail.com',
            password = 'testpass123',
            )
        
        # Get their profiles (auto-created by signal)
        self.profile1 = Profile.objects.get(user = self.user1)
        self.profile2 = Profile.objects.get(user = self.user2)

        # Create test locations
        loc1 = Location.objects.create(
            postalcode = "117417",
            city = "Singapore",
            country = "SG",
            street_address = "13 Computing Drive"
        )
        self.assertEqual(str(loc1), "117417")

        loc2 = Location.objects.create(
            postalcode = "138614",
            city = "Singapore",
            country = "SG",
            street_address = "6 College Avenue East"
        )

        # Set up API client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)

    def tearDown(self):
        patch.stopall()

    def test_profile_creation(self):
        """
        Test that a profile is automatically created when a user is created.
        """
        # These users are created in setUp()
        self.assertIsNotNone(self.profile1)
        self.assertIsNotNone(self.profile2)

        # Confirm that the profile exists in the DB
        self.assertTrue(Profile.objects.filter(user=self.user1).exists())
        self.assertTrue(Profile.objects.filter(user=self.user2).exists())

        # Check that the profile is correctly linked
        profile = Profile.objects.get(user=self.user1)
        self.assertEqual(profile.user.username, 'testuser1')

    def test_profile_update(self):
        """
        Test updating profile information
        """
        url = reverse('profile')
        loc = Location.objects.create(
            postalcode = "117417", 
            city = "Singapore", 
            country = "SG", 
            street_address =  "13 Computing Drive"
            )

        updated_data = {
            "name": "Test test",
            "location": loc.id
        }

        response = self.client.put(url, data = updated_data, format = 'json')

        # Check if successfully updated
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Refresh profile details
        self.profile1.refresh_from_db()
        self.assertEqual(self.profile1.name, "Test test")
        self.assertEqual(self.profile1.location.id, loc.id)

    def test_unique_id_generation(self):
        """
        Test that unique IDs are actually unique
        """
        unique_ids = set()

        # Create 10 random users
        for i in range(10):
            user = User.objects.create_user(username = f'uniqueuser{i}', password = "pass123")
            profile = Profile.objects.get(user = user)

            # Check if unique_id is created
            self.assertIsNotNone(profile.unique_id)
            self.assertEqual(len(profile.unique_id), 8)

            # Ensure it is unique
            self.assertNotIn(profile.unique_id, unique_ids)
            unique_ids.add(profile.unique_id)

    def test_profile_str_representation(self):
        """
        Test the __str__ method of Profile model returns the correct value
        """
        # Case 1: Name is provided
        self.profile1.name = "Test test"
        self.profile1.save()
        self.assertEqual(str(self.profile1), "Test test")

        # Case 2: Name is blank, fall back to user's email
        self.profile2.name = ""
        self.profile2.user.save()
        self.profile2.save()
        self.assertEqual(str(self.profile2), "test2@gmail.com")

    def test_authentication_required(self):
        """
        Test that authentication is required for protected endpoints
        """
        self.client.logout()  # ensure no user is authenticated

        url = reverse('profile')

        response = self.client.get(url)

        self.assertEqual(response.status_code, 401)

    def test_profile_blank_fields(self):
        """
        Test that profile fields can be blank
        """
        # Create a new user
        user = User.objects.create_user(username = 'blanktest', password = 'pass123')

        # Manually create a profile with optional fields left blank
        profile = user.profile

        # Check that the profile is created and blank fields are empty
        self.assertIsNotNone(profile)
        self.assertEqual(profile.name, "")
        self.assertIsNone(profile.location)

    def test_user_creation_api(self):
        """
        Test user registration endpoint creates a new profile
        """
        data = {
            "username": "newuser",
            "email": "newuser@gmail.com",
            "password1": "newpass123",
            "password2": "newpass123"
        }

        response = self.client.post("/api/auth/registration/", data, format = 'json')
        self.assertEqual(response.status_code, 201)

        self.assertTrue(User.objects.filter(username = "newuser").exists())
        self.assertTrue(Profile.objects.filter(user__username = "newuser").exists())
