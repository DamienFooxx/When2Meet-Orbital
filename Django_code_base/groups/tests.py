from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, time, timedelta, datetime
from unittest.mock import patch, MagicMock
from groups.models import Group, GroupMembership
from groups.views import GroupViewSet
from groups.serializers import GroupSerializer, GroupMembershipListSerializer
from accounts.models import Profile, Location


# Create your tests here.
class GroupTestCase(APITestCase):
    """
    # Tests Group Feature Functionalities
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

        # Set up user profiles
        self.profile1 = Profile.objects.get(user=self.user1)
        self.profile2 = Profile.objects.get(user=self.user2)
        self.profile3 = Profile.objects.get(user=self.user3)

        # Set up API client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)

        # Create Group
        url = reverse("group-list")
        data = {"name": "Test Group"}
        response = self.client.post(url, data, format="json")

        # Check that the group was created successfully
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Test Group")

        # Store Group Details
        self.group_id = response.data["id"]
        self.group = Group.objects.get(id=self.group_id)

        self.assertEqual(self.group.creator, self.profile1)
        self.assertTrue(
            GroupMembership.objects.filter(
                group=self.group, profile=self.profile1, role="organiser"
            ).exists()
        )

    def test_invite_user_to_group_using_email(self):
        """
        Test that organiser can invite users to the group
        """
        # Test inviting user
        url = reverse("group-invite-users", kwargs={"pk": self.group.pk})
        data = {"identifiers": ["test2@gmail.com"]}

        initial_invite_response = self.client.post(url, data, format="json")

        self.assertEqual(initial_invite_response.status_code, status.HTTP_200_OK)
        self.assertIn("invited", initial_invite_response.data)
        self.assertIn("test2@gmail.com", initial_invite_response.data["invited"])

    def test_invited_user_can_join_group(self):
        """
        Test that user can join the group after being invited
        """
        url = reverse("group-invite-users", kwargs={"pk": self.group.pk})
        data = {"identifiers": ["test2@gmail.com"]}
        self.client.post(url, data, format="json")

        self.client.force_authenticate(user=self.user2)
        # Fetch the pending GroupMembership for user2
        membership = GroupMembership.objects.get(group=self.group, profile=self.profile2, is_accepted=False)
        join_url = reverse("group-accept-invitation", kwargs={"pk": membership.pk})
        accept_response = self.client.post(join_url, {}, format="json")
        self.assertEqual(accept_response.status_code, status.HTTP_200_OK)
        self.assertIn(
            f'You have joined the group "{self.group.name}".',
            accept_response.data["message"],
        )
        # Check if user is in group
        group_membership_exists = GroupMembership.objects.filter(
            group=self.group,
            profile=self.profile2,
            is_accepted=True,
        ).exists()
        self.assertTrue(group_membership_exists)

    def test_cannot_invite_user_to_group_using_email_as_non_organiser(self):
        """
        Test that non-organisers cannot invite users to the group
        """
        self.client.force_authenticate(user=self.user2)
        url = reverse("group-invite-users", kwargs={"pk": self.group.pk})
        data = {"identifiers": ["test3@gmail.com"]}

        invite_response = self.client.post(url, data, format="json")

        self.assertEqual(invite_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("error", invite_response.data)

        group_membership_exists = GroupMembership.objects.filter(
            group=self.group,
            profile=self.profile3,
            is_accepted=True,
        ).exists()
        self.assertFalse(group_membership_exists)

    def test_join_group_by_code_requires_confirmation(self):
        """
        Test requiring confirmation to join by group code
        """
        self.client.force_authenticate(user=self.user2)
        url = reverse("group-join-by-code")
        group_code = self.group.invite_code
        data = {"invite_code": group_code}

        # Send join request
        request_response = self.client.post(url, data, format="json")
        self.assertEqual(request_response.status_code, status.HTTP_200_OK)
        self.assertTrue(request_response.data.get("confirmation_needed"))
        self.assertEqual(request_response.data["group_info"]["invite_code"], group_code)

    def test_confirm_and_join_group_by_code(self):
        """
        Test Joining the group with a code and organiser needs to accept
        """
        self.client.force_authenticate(user=self.user2)
        url = reverse("group-join-by-code")
        group_code = self.group.invite_code
        data = {"invite_code": group_code, "confirm_join": True}
        self.client.post(url, data, format="json")

        # Test if organiser can accept user
        self.client.force_authenticate(user=self.user1)
        # get the join request
        join_request = GroupMembership.objects.get(
            group=self.group, profile=self.profile2, is_accepted=False, invited_by_organizer=False
        )
        accept_url = reverse("group-accept-join-request", kwargs={"pk": join_request.pk})
        accept_response = self.client.post(accept_url, {}, format="json")
        self.assertEqual(accept_response.status_code, status.HTTP_200_OK)
        self.assertIn("has been added to the group", accept_response.data["message"])

    def test_join_group_by_code_cannot_be_accepted_by_non_organiser(self):
        """
        Test if participants cannot accept requests
        """
        self.client.force_authenticate(user=self.user2)
        url = reverse("group-join-by-code")
        group_code = self.group.invite_code
        data = {"invite_code": group_code, "confirm_join": True}
        self.client.post(url, data, format="json")
        # get the join request
        join_request = GroupMembership.objects.get(
            group=self.group, profile=self.profile2, is_accepted=False, invited_by_organizer=False
        )
        # Test if another member (not organiser) can accept user
        self.client.force_authenticate(user=self.user1)
        # first invite user 3
        url = reverse("group-invite-users", kwargs={"pk": self.group.pk})
        data = {"identifiers": ["test3@gmail.com"]}
        self.client.post(url, data, format="json")
        self.client.force_authenticate(user=self.user3)
        membership3 = GroupMembership.objects.get(group=self.group, profile=self.profile3, is_accepted=False)
        join_url = reverse("group-accept-invitation", kwargs={"pk": membership3.pk})
        self.client.post(join_url, {}, format="json")
        self.client.force_authenticate(user=self.user3)
        accept_url = reverse("group-accept-join-request", kwargs={"pk": join_request.pk})
        accept_response = self.client.post(accept_url, {}, format="json")
        self.assertEqual(accept_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn(
            "Only organisers can accept join requests.", accept_response.data["error"]
        )

    def test_join_group_if_already_member(self):
        """
        Test if a user cannot send another request to join the group again when inside
        """
        # user 2 joins group
        self.client.force_authenticate(user=self.user1)
        url = reverse("group-invite-users", kwargs={"pk": self.group.pk})
        data = {"identifiers": ["test2@gmail.com"]}
        self.client.post(url, data, format="json")
        self.client.force_authenticate(user=self.user2)
        membership = GroupMembership.objects.get(group=self.group, profile=self.profile2, is_accepted=False)
        join_url = reverse("group-accept-invitation", kwargs={"pk": membership.pk})
        self.client.post(join_url, {}, format="json")
        # try to join again
        self.client.force_authenticate(user=self.user2)
        url = reverse("group-join-by-code")
        group_code = self.group.invite_code
        data = {"invite_code": group_code, "confirm_join": True}
        request_response = self.client.post(url, data, format="json")
        # Check if error message pops up properly
        self.assertEqual(request_response.status_code, status.HTTP_200_OK)
        self.assertIn("Already a group member.", request_response.data["error"])

    def test_leave_group_as_participant(self):
        """
        Test that a participant can leave the group and is removed from membership
        """
        # user 2 joins group
        self.client.force_authenticate(user=self.user1)
        url = reverse("group-invite-users", kwargs={"pk": self.group.pk})
        data = {"identifiers": ["test2@gmail.com"]}
        self.client.post(url, data, format="json")
        self.client.force_authenticate(user=self.user2)
        join_url = reverse("group-accept-invitation", kwargs={"pk": self.group.pk})
        self.client.post(join_url, {}, format="json")

        self.client.force_authenticate(user=self.user2)
        url = reverse("group-leave-group", kwargs={"pk": self.group.pk})
        response = self.client.post(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("You have left the group", response.data.get("message", ""))
        self.assertFalse(
            GroupMembership.objects.filter(
                group=self.group, profile=self.profile2
            ).exists()
        )

    def test_leave_group_as_last_member_deletes_group(self):
        """
        Test that if the last member leaves, the group is deleted
        """
        self.client.force_authenticate(user=self.user1)
        url = reverse("group-leave-group", kwargs={"pk": self.group.pk})
        # The test creates a group with user1 as the only member.
        response = self.client.post(url, {"confirm_delete": True}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(
            f'Group "{self.group.name}" deleted as you were the last member.',
            response.data.get("message", ""),
        )
        self.assertFalse(Group.objects.filter(id=self.group.id).exists())

    def test_last_organiser_cannot_leave(self):
        """
        Test that the last organiser cannot leave the group
        """
        # Add user2 as a member
        GroupMembership.objects.create(
            group=self.group, profile=self.profile2, role="member", is_accepted=True
        )
        # User 1 is the only organiser
        self.client.force_authenticate(user=self.user1)
        url = reverse("group-leave-group", kwargs={"pk": self.group.pk})
        response = self.client.post(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("You are the last organiser", response.data.get("error", ""))

    def test_list_members_sorted(self):
        """
        Test that the group members are listed in sorted order (e.g., by join date or name)
        """
        # Add user2 as a member
        GroupMembership.objects.create(
            group=self.group, profile=self.profile2, role="member", is_accepted=True
        )
        url = reverse("group-list-members", kwargs={"pk": self.group.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        # user1 (organiser) should be first
        self.assertEqual(response.data[0]["profile"]["user"], "testuser1")

    def test_group_size_limit(self):
        """
        Test that the group cannot exceed its size limit
        """
        self.group.max_size = 2
        self.group.save()

        # Add user2, group is now full
        GroupMembership.objects.create(
            group=self.group, profile=self.profile2, role="member", is_accepted=True
        )

        # Try to add user3
        self.client.force_authenticate(user=self.user3)
        url = reverse("group-join-by-code")
        data = {"invite_code": self.group.invite_code, "confirm_join": True}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("Group is full", response.data.get("error", ""))

    def test_join_group_invalid_invite_code(self):
        """
        Test that joining with an invalid invite code fails
        """
        self.client.force_authenticate(user=self.user2)
        url = reverse("group-join-by-code")
        data = {"invite_code": "invalidcode"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("Invalid invite code", response.data.get("error", ""))

    def test_join_group_full_group(self):
        """
        Test that joining a full group is not allowed
        """
        self.group.max_size = 10
        self.group.save()
        # Create 9 more users and add them to the group
        for i in range(9):
            user = User.objects.create_user(
                username=f"user{i+4}", password="password123"
            )
            GroupMembership.objects.create(
                group=self.group, profile=user.profile, role="member", is_accepted=True
            )

        self.client.force_authenticate(user=self.user2)
        url = reverse("group-join-by-code")
        data = {"invite_code": self.group.invite_code, "confirm_join": True}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("Group is full", response.data.get("error", ""))

    def test_join_group_invalid_confirmation(self):
        """
        Test that confirming with an invalid token or confirmation fails
        """
        self.client.force_authenticate(user=self.user2)
        # Use a non-existent GroupMembership id
        invalid_pk = 999999
        url = reverse("group-accept-invitation", kwargs={"pk": invalid_pk})
        data = {"confirmation_token": "invalidtoken"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class GroupsViewsTestCase(APITestCase):
    """
    Test suite for groups views
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

        # Create group
        self.group = Group.objects.create(
            name="Test Group",
            description="Test Description",
            creator=self.profile1,
            max_size=5
        )

        # Create group membership for creator
        GroupMembership.objects.create(
            group=self.group,
            profile=self.profile1,
            role="organiser",
            is_accepted=True
        )

        # Set up API client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)

    def tearDown(self):
        patch.stopall()

    def test_group_viewset_create(self):
        """Test GroupViewSet create"""
        data = {
            "name": "New Group",
            "description": "New Description",
            "max_size": 10
        }
        
        url = reverse("group-list")
        response = self.client.post(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Group.objects.count(), 2)
        self.assertEqual(response.data["name"], "New Group")

    def test_group_viewset_destroy_as_organiser(self):
        """Test GroupViewSet destroy as organiser"""
        url = reverse("group-detail", kwargs={"pk": self.group.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Group.objects.filter(id=self.group.id).exists())

    def test_group_viewset_destroy_as_non_organiser(self):
        """Test GroupViewSet destroy as non-organiser"""
        # Add user2 as member
        GroupMembership.objects.create(
            group=self.group,
            profile=self.profile2,
            role="member",
            is_accepted=True
        )
        
        self.client.force_authenticate(user=self.user2)
        url = reverse("group-detail", kwargs={"pk": self.group.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Group.objects.filter(id=self.group.id).exists())

    def test_group_viewset_list_members(self):
        """Test GroupViewSet list_members action"""
        # Add user2 as member
        GroupMembership.objects.create(
            group=self.group,
            profile=self.profile2,
            role="member",
            is_accepted=True
        )
        
        url = reverse("group-list-members", kwargs={"pk": self.group.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        # Organiser should be first
        self.assertEqual(response.data[0]["role"], "organiser")

    def test_group_viewset_list_members_exception(self):
        """Test GroupViewSet list_members with exception"""
        # Mock the get_object method to raise an exception
        with patch.object(GroupViewSet, 'get_object', side_effect=Exception("Test error")):
            url = reverse("group-list-members", kwargs={"pk": self.group.pk})
            response = self.client.get(url)
            
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertIn("error", response.data)

    def test_group_viewset_leave_group_as_member(self):
        """Test GroupViewSet leave_group as member"""
        # Add user2 as member
        GroupMembership.objects.create(
            group=self.group,
            profile=self.profile2,
            role="member",
            is_accepted=True
        )
        
        self.client.force_authenticate(user=self.user2)
        url = reverse("group-leave-group", kwargs={"pk": self.group.pk})
        response = self.client.post(url, {}, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("You have left the group", response.data["message"])
        self.assertFalse(
            GroupMembership.objects.filter(
                group=self.group, profile=self.profile2
            ).exists()
        )

    def test_group_viewset_leave_group_as_non_member(self):
        """Test GroupViewSet leave_group as non-member"""
        # Create a user who is not a member of the group
        non_member = User.objects.create_user(
            username="nonmember",
            email="nonmember@example.com",
            password="testpass123"
        )
        # Use get_or_create to avoid duplicate profile creation
        profile, created = Profile.objects.get_or_create(user=non_member)
        
        self.client.force_authenticate(user=non_member)
        
        url = reverse("group-leave-group", kwargs={"pk": self.group.id})
        response = self.client.post(url, {}, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Not a member of the group", response.data["error"])

    def test_group_viewset_leave_group_as_last_organiser_with_other_members(self):
        """Test GroupViewSet leave_group as last organiser with other members"""
        # Add user2 as member
        GroupMembership.objects.create(
            group=self.group,
            profile=self.profile2,
            role="member",
            is_accepted=True
        )
        
        url = reverse("group-leave-group", kwargs={"pk": self.group.pk})
        response = self.client.post(url, {}, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("last organiser", response.data["error"])

    def test_group_viewset_leave_group_as_last_member_deletes_group(self):
        """Test GroupViewSet leave_group as last member deletes group"""
        url = reverse("group-leave-group", kwargs={"pk": self.group.pk})
        response = self.client.post(url, {}, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("deleted as you were the last member", response.data["message"])
        self.assertFalse(Group.objects.filter(id=self.group.id).exists())

    def test_group_viewset_invitations(self):
        """Test GroupViewSet invitations action"""
        url = reverse("group-invitations")
        
        # Create a separate group for testing invitations
        test_group = Group.objects.create(
            name="Test Group 2",
            description="Test Description 2",
            creator=self.profile2,
            max_size=5
        )
        
        # Create an invitation for the authenticated user (user1)
        GroupMembership.objects.create(
            group=test_group,
            profile=self.user1.profile,
            role="invited",
            is_accepted=False,
            invited_by_organizer=True
        )
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_group_viewset_invite_users(self):
        """Test GroupViewSet invite_users action"""
        data = {"identifiers": ["test2@gmail.com", "test3@gmail.com"]}
        
        url = reverse("group-invite-users", kwargs={"pk": self.group.pk})
        response = self.client.post(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(GroupMembership.objects.filter(group=self.group, is_accepted=False).count(), 2)

    def test_group_viewset_invite_users_as_non_organiser(self):
        """Test GroupViewSet invite_users as non-organiser"""
        # Add user2 as member
        GroupMembership.objects.create(
            group=self.group,
            profile=self.profile2,
            role="member",
            is_accepted=True
        )
        
        self.client.force_authenticate(user=self.user2)
        data = {"identifiers": ["test3@gmail.com"]}
        
        url = reverse("group-invite-users", kwargs={"pk": self.group.pk})
        response = self.client.post(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("Only organisers can invite users", response.data["error"])

    def test_group_viewset_invite_users_group_full(self):
        """Test GroupViewSet invite_users when group is full"""
        # Add users to reach max size
        for i in range(4):  # Already has 1 member, need 4 more to reach max_size=5
            user = User.objects.create_user(
                username=f"user{i}",
                email=f"user{i}@gmail.com",
                password="testpass123"
            )
            profile = Profile.objects.get(user=user)
            GroupMembership.objects.create(
                group=self.group,
                profile=profile,
                role="member",
                is_accepted=True
            )
        
        data = {"identifiers": ["test2@gmail.com"]}
        
        url = reverse("group-invite-users", kwargs={"pk": self.group.pk})
        response = self.client.post(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # The view doesn't check group size during invitation, it's checked during join

    def test_group_viewset_join_by_code(self):
        """Test GroupViewSet join_by_code action"""
        data = {"invite_code": self.group.invite_code, "confirm_join": True}
        
        self.client.force_authenticate(user=self.user2)
        url = reverse("group-join-by-code")
        response = self.client.post(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("request to join group", response.data["message"])

    def test_group_viewset_join_by_code_invalid_code(self):
        """Test GroupViewSet join_by_code with invalid code"""
        data = {"invite_code": "invalid_code", "confirm_join": True}
        
        self.client.force_authenticate(user=self.user2)
        url = reverse("group-join-by-code")
        response = self.client.post(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("Invalid invite code", response.data["error"])

    def test_group_viewset_join_by_code_already_member(self):
        """Test GroupViewSet join_by_code when already a member"""
        # Add user2 as member
        GroupMembership.objects.create(
            group=self.group,
            profile=self.profile2,
            role="member",
            is_accepted=True
        )
        
        data = {"invite_code": self.group.invite_code, "confirm_join": True}
        
        self.client.force_authenticate(user=self.user2)
        url = reverse("group-join-by-code")
        response = self.client.post(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Already a group member", response.data["error"])

    def test_group_viewset_join_by_code_group_full(self):
        """Test GroupViewSet join_by_code when group is full"""
        # Add users to reach max size
        for i in range(4):  # Already has 1 member, need 4 more to reach max_size=5
            user = User.objects.create_user(
                username=f"user{i}",
                email=f"user{i}@gmail.com",
                password="testpass123"
            )
            profile = Profile.objects.get(user=user)
            GroupMembership.objects.create(
                group=self.group,
                profile=profile,
                role="member",
                is_accepted=True
            )
        
        data = {"invite_code": self.group.invite_code, "confirm_join": True}
        
        self.client.force_authenticate(user=self.user2)
        url = reverse("group-join-by-code")
        response = self.client.post(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("Group is full", response.data["error"])

    def test_group_viewset_accept_invitation(self):
        """Test GroupViewSet accept_invitation action"""
        # Create invitation for user2
        membership = GroupMembership.objects.create(
            group=self.group,
            profile=self.profile2,
            role="member",
            is_accepted=False,
            invited_by_organizer=True
        )
        
        self.client.force_authenticate(user=self.user2)
        url = reverse("group-accept-invitation", kwargs={"pk": membership.pk})
        response = self.client.post(url, {}, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("You have joined the group", response.data["message"])
        
        membership.refresh_from_db()
        self.assertTrue(membership.is_accepted)

    def test_group_viewset_decline_invitation(self):
        """Test GroupViewSet decline_invitation action"""
        # Create invitation for user2
        membership = GroupMembership.objects.create(
            group=self.group,
            profile=self.profile2,
            role="member",
            is_accepted=False,
            invited_by_organizer=True
        )
        
        self.client.force_authenticate(user=self.user2)
        url = reverse("group-decline-invitation", kwargs={"pk": membership.pk})
        response = self.client.post(url, {}, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("You have declined the invitation", response.data["message"])
        
        self.assertFalse(
            GroupMembership.objects.filter(id=membership.id).exists()
        )

    def test_group_viewset_accept_join_request(self):
        """Test GroupViewSet accept_join_request action"""
        # Create join request for user2
        membership = GroupMembership.objects.create(
            group=self.group,
            profile=self.profile2,
            role="member",
            is_accepted=False,
            invited_by_organizer=False
        )
        
        url = reverse("group-accept-join-request", kwargs={"pk": membership.pk})
        response = self.client.post(url, {}, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("has been added to the group", response.data["message"])
        
        membership.refresh_from_db()
        self.assertTrue(membership.is_accepted)

    def test_group_viewset_accept_join_request_as_non_organiser(self):
        """Test GroupViewSet accept_join_request as non-organiser"""
        # Add user2 as member
        GroupMembership.objects.create(
            group=self.group,
            profile=self.profile2,
            role="member",
            is_accepted=True
        )
        
        # Create join request for user3
        membership = GroupMembership.objects.create(
            group=self.group,
            profile=self.profile3,
            role="member",
            is_accepted=False,
            invited_by_organizer=False
        )
        
        self.client.force_authenticate(user=self.user2)
        url = reverse("group-accept-join-request", kwargs={"pk": membership.pk})
        response = self.client.post(url, {}, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("Only organisers can accept join requests", response.data["error"])

    def test_group_viewset_decline_join_request(self):
        """Test GroupViewSet decline_join_request action"""
        # Create join request for user2
        membership = GroupMembership.objects.create(
            group=self.group,
            profile=self.profile2,
            role="member",
            is_accepted=False,
            invited_by_organizer=False
        )
        
        url = reverse("group-decline-join-request", kwargs={"pk": membership.pk})
        response = self.client.post(url, {}, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("has been declined", response.data["message"])
        
        self.assertFalse(
            GroupMembership.objects.filter(id=membership.id).exists()
        )

    def test_group_viewset_decline_join_request_as_non_organiser(self):
        """Test GroupViewSet decline_join_request as non-organiser"""
        # Add user2 as member
        GroupMembership.objects.create(
            group=self.group,
            profile=self.profile2,
            role="member",
            is_accepted=True
        )
        
        # Create join request for user3
        membership = GroupMembership.objects.create(
            group=self.group,
            profile=self.profile3,
            role="member",
            is_accepted=False,
            invited_by_organizer=False
        )
        
        self.client.force_authenticate(user=self.user2)
        url = reverse("group-decline-join-request", kwargs={"pk": membership.pk})
        response = self.client.post(url, {}, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("Only organisers can decline join requests", response.data["error"])
