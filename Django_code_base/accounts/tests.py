from django.urls import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from accounts.models import Profile, Location
from accounts.views import CheckUserByEmail, GoogleLogin, ProfileView, GoogleCalendarFreeBusyView
from unittest.mock import patch, MagicMock
from allauth.socialaccount.models import SocialAccount, SocialToken, SocialApp
from django.contrib.auth import get_user_model


class LocationTestCase(APITestCase):
    """
    Test suite for location authentication
    """

    @patch("accounts.models.geolocator.geocode")
    def test_valid_location_save_coordinates(self, mock_geocode):
        mock_location = MagicMock()
        mock_location.latitude = 1.3521
        mock_location.longitude = 103.8198
        mock_geocode.return_value = mock_location

        loc = Location(
            postalcode="117417",
            city="Singapore",
            country="SG",
            street_address="13 Computing Drive",
        )
        loc.save()

        self.assertIsNotNone(loc.latitude)
        self.assertIsNotNone(loc.longitude)

    @patch("accounts.models.geolocator.geocode")
    def test_invalid_location_save_coordinates(self, mock_geocode):
        mock_geocode.return_value = None

        loc = Location(
            postalcode="000000",
            city="Nowhere",
            country="SG",
            street_address="Empty Street",
        )

        with self.assertRaises(ValidationError):
            loc.save()

    @patch("accounts.models.geolocator.geocode")
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
            postalcode="117417",
            city="Singapore",
            country="SG",
            street_address="13 Computing Drive",
        )
        self.assertEqual(str(loc1), "117417")

        # Case 2: postalcode is blank, fallback to street_address
        loc2 = Location.objects.create(
            postalcode="", city="Singapore", street_address="6 College Avenue East"
        )
        self.assertEqual(str(loc2), "6 College Avenue East")


class AccountTestCase(APITestCase):
    """
    Test suite for the accounts app functionality
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

        # Get their profiles (auto-created by signal)
        self.profile1 = Profile.objects.get(user=self.user1)
        self.profile2 = Profile.objects.get(user=self.user2)

        # Create test locations
        loc1 = Location.objects.create(
            postalcode="117417",
            city="Singapore",
            country="SG",
            street_address="13 Computing Drive",
        )
        self.assertEqual(str(loc1), "117417")

        loc2 = Location.objects.create(
            postalcode="138614",
            city="Singapore",
            country="SG",
            street_address="6 College Avenue East",
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
        self.assertEqual(profile.user.username, "testuser1")

    def test_profile_update(self):
        """
        Test updating profile information
        """
        url = reverse("profile")
        loc = Location.objects.create(
            postalcode="117417",
            city="Singapore",
            country="SG",
            street_address="13 Computing Drive",
        )

        updated_data = {"name": "Test test", "location": loc.id}

        response = self.client.put(url, data=updated_data, format="json")

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
            user = User.objects.create_user(
                username=f"uniqueuser{i}", password="pass123"
            )
            profile = Profile.objects.get(user=user)

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

        url = reverse("profile")

        response = self.client.get(url)

        self.assertEqual(response.status_code, 401)

    def test_profile_blank_fields(self):
        """
        Test that profile fields can be blank
        """
        # Create a new user
        user = User.objects.create_user(username="blanktest", password="pass123")

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
            "password2": "newpass123",
        }

        response = self.client.post("/api/auth/registration/", data, format="json")
        self.assertEqual(response.status_code, 201)

        self.assertTrue(User.objects.filter(username="newuser").exists())
        self.assertTrue(Profile.objects.filter(user__username="newuser").exists())


class AccountViewsTestCase(APITestCase):
    """
    Test suite for account views functionality
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

        # Get their profiles (auto-created by signal)
        self.profile1 = Profile.objects.get(user=self.user1)
        self.profile2 = Profile.objects.get(user=self.user2)

        # Set up API client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)

    def tearDown(self):
        patch.stopall()

    def test_check_user_by_email_exists(self):
        """Test checking if a user exists by email"""
        url = reverse("check_user")
        response = self.client.get(url, {"email": "test1@gmail.com"})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["exists"])

    def test_check_user_by_email_not_exists(self):
        """Test checking if a user doesn't exist by email"""
        url = reverse("check_user")
        response = self.client.get(url, {"email": "nonexistent@example.com"})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["exists"])

    def test_check_user_by_email_no_email(self):
        """Test checking user by email without providing email"""
        url = reverse("check_user")
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_check_user_by_email_empty_email(self):
        """Test checking user by email with empty email"""
        url = reverse("check_user")
        response = self.client.get(url, {"email": ""})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_check_user_by_email_whitespace_email(self):
        """Test checking user by email with whitespace-only email"""
        url = reverse("check_user")
        response = self.client.get(url, {"email": "   "})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_check_user_by_email_case_insensitive(self):
        """Test that email checking is case insensitive"""
        url = reverse("check_user")
        response = self.client.get(url, {"email": "TEST1@GMAIL.COM"})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["exists"])

    def test_check_user_by_email_unauthenticated(self):
        """Test that unauthenticated users cannot check emails"""
        self.client.force_authenticate(user=None)
        url = reverse("check_user")
        response = self.client.get(url, {"email": "test1@gmail.com"})
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('accounts.views.User.objects.filter')
    def test_check_user_by_email_exception_handling(self, mock_filter):
        """Test exception handling in check user by email"""
        mock_filter.side_effect = Exception("Database error")
        
        url = reverse("check_user")
        response = self.client.get(url, {"email": "test1@gmail.com"})
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("error", response.data)

    def test_profile_view_get(self):
        """Test getting user profile"""
        url = reverse("profile")
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("name", response.data)
        self.assertIn("email", response.data)

    def test_profile_view_put(self):
        """Test updating user profile"""
        url = reverse("profile")
        loc = Location.objects.create(
            postalcode="117417",
            city="Singapore",
            country="SG",
            street_address="13 Computing Drive",
        )
        
        update_data = {
            "name": "Updated Name",
            "location": loc.id
        }
        
        response = self.client.put(url, update_data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile1.refresh_from_db()
        self.assertEqual(self.profile1.name, "Updated Name")

    def test_profile_view_put_invalid_location(self):
        """Test updating profile with invalid location"""
        url = reverse("profile")
        update_data = {
            "name": "Updated Name",
            "location": 99999  # Non-existent location ID
        }
        
        response = self.client.put(url, update_data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_profile_view_unauthenticated(self):
        """Test that unauthenticated users cannot access profile"""
        self.client.logout()
        url = reverse("profile")
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        response = self.client.put(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_view_get_exception(self):
        """Test exception handling in profile view get"""
        url = reverse("profile")
        
        with patch('accounts.views.Profile.objects.get') as mock_get:
            mock_get.side_effect = Exception("Database error")
            
            response = self.client.get(url)
        
        # The view should handle the exception and return 500
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_profile_view_put_exception(self):
        """Test exception handling in profile view put"""
        url = reverse("profile")
        
        with patch('accounts.views.Profile.objects.get') as mock_get:
            mock_get.side_effect = Exception("Database error")
            
            response = self.client.put(url, {"name": "test"}, format="json")
        
        # The view should handle the exception and return 500
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_google_calendar_free_busy_success(self):
        """Test successful Google Calendar free busy request"""
        # Create a social account for the user
        from allauth.socialaccount.models import SocialAccount, SocialToken, SocialApp
        
        # Create a social app
        social_app = SocialApp.objects.create(
            provider="google",
            name="Google",
            client_id="test_client_id",
            secret="test_secret"
        )
        
        # Create a social account
        social_account = SocialAccount.objects.create(
            user=self.user1,
            provider="google",
            uid="test_uid"
        )
        
        # Create a social token
        social_token = SocialToken.objects.create(
            account=social_account,
            app=social_app,
            token="test_access_token"
        )
        
        url = reverse("google_calendar_freebusy")
        
        with patch('requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "calendars": {
                    "primary": {
                        "busy": [
                            {
                                "start": "2024-01-01T10:00:00Z",
                                "end": "2024-01-01T11:00:00Z"
                            }
                        ]
                    }
                }
            }
            mock_post.return_value = mock_response
            
            response = self.client.post(url, {
                "start": "2024-01-01T00:00:00Z",
                "end": "2024-01-01T23:59:59Z"
            }, format="json")
    
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("busy", response.data)

    def test_google_calendar_free_busy_no_token(self):
        """Test Google Calendar free busy without token"""
        url = reverse("google_calendar_freebusy")
        
        with patch('availcalendar.tasks.get_google_token') as mock_get_token:
            mock_get_token.return_value = None
            
            response = self.client.post(url, {
                "start": "2024-01-01T00:00:00Z",
                "end": "2024-01-01T23:59:59Z"
            }, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Google account not connected", response.data["error"])

    def test_google_calendar_free_busy_no_social_account(self):
        """Test Google Calendar free busy without social account"""
        # Create a user without social account
        user_without_social = User.objects.create_user(
            username="nosocial",
            email="nosocial@example.com",
            password="testpass123"
        )
        # Use get_or_create to avoid duplicate profile creation
        profile, created = Profile.objects.get_or_create(user=user_without_social)
        
        self.client.force_authenticate(user=user_without_social)
        
        url = reverse("google_calendar_freebusy")
        
        with patch('availcalendar.tasks.get_google_token') as mock_get_token:
            mock_get_token.return_value = None
            
            response = self.client.post(url, {
                "start": "2024-01-01T00:00:00Z",
                "end": "2024-01-01T23:59:59Z"
            }, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Google account not connected", response.data["error"])

    def test_google_calendar_free_busy_api_error(self):
        """Test Google Calendar free busy with API error"""
        # Create a social account for the user
        from allauth.socialaccount.models import SocialAccount, SocialToken, SocialApp
        
        # Create a social app
        social_app = SocialApp.objects.create(
            provider="google",
            name="Google",
            client_id="test_client_id",
            secret="test_secret"
        )
        
        # Create a social account
        social_account = SocialAccount.objects.create(
            user=self.user1,
            provider="google",
            uid="test_uid"
        )
        
        # Create a social token
        social_token = SocialToken.objects.create(
            account=social_account,
            app=social_app,
            token="test_access_token"
        )
        
        url = reverse("google_calendar_freebusy")
        
        with patch('requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.json.return_value = {"error": "API Error"}
            mock_post.return_value = mock_response
            
            response = self.client.post(url, {
                "start": "2024-01-01T00:00:00Z",
                "end": "2024-01-01T23:59:59Z"
            }, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("Failed to fetch from Google Calendar", response.data["error"])

    def test_google_calendar_free_busy_exception(self):
        """Test exception handling in Google Calendar free busy"""
        # Create a social account for the user
        from allauth.socialaccount.models import SocialAccount, SocialToken, SocialApp
        
        # Create a social app
        social_app = SocialApp.objects.create(
            provider="google",
            name="Google",
            client_id="test_client_id",
            secret="test_secret"
        )
        
        # Create a social account
        social_account = SocialAccount.objects.create(
            user=self.user1,
            provider="google",
            uid="test_uid"
        )
        
        # Create a social token
        social_token = SocialToken.objects.create(
            account=social_account,
            app=social_app,
            token="test_access_token"
        )
        
        url = reverse("google_calendar_freebusy")
        
        with patch('requests.post') as mock_post:
            # Mock the requests.post to raise an exception
            mock_post.side_effect = Exception("Token error")
            
            # The test should verify that the exception is raised
            # and that Django's exception handler properly handles it
            with self.assertRaises(Exception) as context:
                response = self.client.post(url, {
                    "start": "2024-01-01T00:00:00Z",
                    "end": "2024-01-01T23:59:59Z"
                }, format="json")
            
            # Verify the exception message
            self.assertIn("Token error", str(context.exception))

    def test_google_calendar_free_busy_unauthenticated(self):
        """Test that unauthenticated users cannot access Google Calendar free busy"""
        self.client.force_authenticate(user=None)
        url = reverse("google_calendar_freebusy")
        response = self.client.get(url, {
            "start": "2024-01-01T00:00:00Z",
            "end": "2024-01-01T23:59:59Z"
        })
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
