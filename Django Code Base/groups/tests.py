from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from groups.models import Group, GroupMembership
from accounts.models import Profile, Location
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

# Create your tests here.
class GroupTestCase(APITestCase):
    """
    # Tests Group Feature Functionalities
    """

    def login_as(self, username, password = "testpass123"):
        """
        Helper for switching user
        """
        self.client.logout()
        self.client.login(username = username, password = password)

    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(username = 'testuser1', password = 'testpass123')
        self.user2 = User.objects.create_user(username = 'testuser2', password = 'testpass123')
        self.user3 = User.objects.create_user(username = 'testuser3', password = 'testpass123')

        # Create test locations
        loc1 = Location.objects.create(
            postalcode = "117417",
            city = "Singapore",
            country = "SG",
            street_address = "13 Computing Drive"
        )
        self.assertEqual(str(loc1), "123456")

        loc2 = Location.objects.create(
            postalcode = "138614",
            city = "Singapore",
            country = "SG",
            street_address = "6 College Avenue East"
        )

        # Set up user profiles
        self.profile1 = Profile.objects.create(
            user = self.user1,
            name = "Test1",
            email = "test1@gmail.com",
            location = loc1.id,
        )

        self.profile2 = Profile.objects.create(
            user = self.user2,
            name = "Test2",
            email = "test2@gmail.com",
            location = loc2.id
        )

        self.profile3 = Profile.objects.create(
            user = self.user3,
            name = "Test3",
            email = "test3@gmail.com",
            location = loc2.id,
        )

        # Set up API client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)

        # Create Group
        self.login_as("testuser1")
        url = reverse('group')
        data = {
            "name": "Test Group"
        }
        response = self.client.post(url, data, format = 'json')

        # Check that the group was created successfully
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Test Group')

        self.assertEqual(group.creator, self.user.profile)
        self.assertTrue(
            GroupMembership.objects.filter(
                group = group, 
                profile = self.profile1,
                role = 'organiser'
                ).exists()
        )

        # Store Group Details
        group_id = response.data['id']
        group = Group.objects.get(id = group_id)
        group_url = reverse('group', kwargs = {'pk': group_id})

    def test_invite_user_to_group_using_email(self):
        """
        Test that organiser can invite users to the group
        """
        # Test inviting user
        url = reverse('group-invite')
        data = {"identifier": "test2@gmail.com"}

        initial_invite_response = self.client.post(url, data, format = 'json')

        self.assertEqual(initial_invite_response.status_code, status.HTTP_200_OK)
        self.assertIn("invited", initial_invite_response.data)
        self.assertIn("test2@gmail.com", initial_invite_response.data["invited"])

    def test_invited_user_can_join_group(self):
        """
        Test that user can join the group after being invited
        """
        url = reverse('group-invite')
        data = {"identifier": "test2@gmail.com"}
        initial_invite_response = self.client.post(url, data, format = 'json')

        self.login_as("testuser2")
        join_url = reverse('group-accept-invitation')
        accept_response = self.client.post(join_url, {}, format = 'json')
        self.assertEqual(accept_response.status_code, status.HTTP_200_OK)
        self.assertIn(f'You have joined the group Test Group.', accept_response.data)

        # Check if user is in group
        group_membership_exists = GroupMembership.objects.filter(
            group_id = self.group_id,
            profile = self.profile2,
            is_accepted = True,
            ).exists()
        self.assertTrue(group_membership_exists)

    def test_cannot_invite_user_to_group_using_email_as_non_organiser(self):
        """
        Test that non-organisers cannot invite users to the group
        """
        self.login_as("testuser2")
        url = reverse('group-invite')
        data = {"identifier": "test3@gmail.com"}

        invite_response = self.client.post(url, data, format = 'json')

        self.assertIn(invite_response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_400_BAD_REQUEST])
        self.assertIn("error", invite_response.data)

        group_membership_exists = GroupMembership.objects.filter(
            group_id = self.group_id,
            profile = self.profile3,
            is_accepted = True,
        ).exists()
        self.assertFalse(group_membership_exists)

    def test_join_group_by_code_requires_confirmation(self):
        """
        Test requiring confirmation to join by group code
        """
        self.login_as("testuser1")
        url = reverse('group-join-by-code')
        group_code = self.group.invite_code
        data = {'code': "group_code"}
        
        # Send join request
        request_response = self.client.post(url, data, format = 'json')
        self.assertEqual(request_response.status_code, status.HTTP_200_OK)
        self.assertTrue(request_response.data.get("confirmation_needed"))
        self.assertTrue(request_response.data["group_info"]["invite_code"], group_code)

    def test_confirm_and_join_group_by_code(self):
        """
        Test Joining the group with a code and organiser needs to accept
        """
        self.login_as("testuser2")
        url = reverse('group-join-by-code')
        group_code = self.group.invite_code
        data = {'code': "group_code"}
        request_response = self.client.post(url, data, format = 'json')

        # Test if organiser can accept user
        self.login_as("testuser1")
        accept_url = reverse("group-accept-request")
        accept_response = self.client.post(accept_url, {}, format = 'json')
        self.assertEqual(accept_response.status_code, status.HTTP_200_OK)
        self.assertIn(
            "User testuser2 has been added to the group Test Group",
            accept_response.data["message"]
            )

    def test_join_group_by_code_cannot_be_accepted_by_non_organiser(self):
        """
        Test if participants cannot accept requests
        """
        self.login_as("testuser2")
        url = reverse('group-join-by-code')
        group_code = self.group.invite_code
        data = {'code': "group_code"}
        request_response = self.client.post(url, data, format = 'json')

        # Test if organiser can accept user
        self.login_as("testuser1")
        invite_url = reverse('group-invite')
        data = {"identifier": "test3@gmail.com"}
        initial_invite_response = self.client.post(invite_url, data, format = 'json')

        accept_url = reverse("group-accept-request")
        self.login_as("testuser3")
        accept_response = self.client.post(accept_url, {}, format = 'json')
        self.assertEqual(accept_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn(
            "Only organisers can accept join requests.",
            accept_response.data["error"]
            )

    def test_join_group_if_already_member(self):
        """
        Test if a user cannot send another request to join the group again when inside
        """
        self.login_as("testuser2")
        url = reverse('group-join-by-code')
        group_code = self.group.invite_code
        data = {'code': "group_code"}
        request_response = self.client.post(url, data, format = 'json')
        # Check if error message pops up properly
        self.assertEqual(request_response.status_code, status.HTTP_200_OK)
        self.assertIn(
            "Already a group member",
            request_response.data["error"]
            )

    def test_leave_group_as_participant(self):
        """
        Test that a participant can leave the group and is removed from membership
        """
        self.login_as("testuser2")
        url = reverse('group-leave')
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("You have left the group", response.data.get("message", ""))
        self.assertFalse(GroupMembership.objects.filter(group = self.group, profile = self.profile2).exists())

    def test_leave_group_as_last_member_deletes_group(self):
        """
        Test that if the last member leaves, the group is deleted
        """
        self.login_as("testuser1")
        url = reverse('group-leave')
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Group deleted", response.data.get("message", ""))
        self.assertFalse(Group.objects.filter(id = self.group.id).exists())

    def test_last_organiser_cannot_leave(self):
        """
        Test that the last organiser cannot leave the group
        """
        self.login_as("testuser1")
        url = reverse('group-leave')
        response = self.client.post(url, {}, format = 'json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("last organiser", response.data.get("error", ""))
        self.assertTrue(GroupMembership.objects.filter(group = self.group, profile = self.profile1, role = 'organiser').exists())

    def test_list_members_sorted(self):
        """
        Test that the group members are listed in sorted order (e.g., by join date or name)
        """
        self.login_as("testuser1")
        url = reverse('group-members')
        response = self.client.get(url, format = 'json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        members = response.data.get('members', [])
        sorted_members = sorted(members, key = lambda m: m['name'])
        self.assertEqual(members, sorted_members)

    def test_group_size_limit(self):
        """
        Test that the group cannot exceed its size limit
        """
        self.login_as("testuser1")
        url = reverse('group-invite')
        # Simulate group size limit reached
        for i in range(10):
            User.objects.create_user(username = f'user{i+4}', password = 'testpass123')
            Profile.objects.create(user = User.objects.get(username = f'user{i+4}'), name = f'User{i+4}', email = f'user{i+4}@gmail.com', location = self.profile1.location)
            data = {"identifier": f'user{i+4}@gmail.com'}
            self.client.post(url, data, format = 'json')
        # Now try to add one more
        data = {"identifier": "overflow@gmail.com"}
        response = self.client.post(url, data, format = 'json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("group is full", response.data.get("error", ""))

    def test_join_group_invalid_invite_code(self):
        """
        Test that joining with an invalid invite code fails
        """
        self.login_as("testuser2")
        url = reverse('group-join-by-code')
        data = {'code': "invalidcode"}
        response = self.client.post(url, data, format = 'json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid invite code", response.data.get("error", ""))

    def test_join_group_full_group(self):
        """
        Test that joining a full group is not allowed
        """
        self.login_as("testuser2")
        url = reverse('group-join-by-code')
        # Simulate group is full
        self.group.size_limit = 10
        self.group.save()
        for i in range(10):
            User.objects.create_user(username=f'user{i+4}', password='testpass123')
            Profile.objects.create(user=User.objects.get(username=f'user{i+4}'), name=f'User{i+4}', email=f'user{i+4}@gmail.com', location=self.profile1.location)
            GroupMembership.objects.create(group = self.group, profile=Profile.objects.get(user__username=f'user{i+4}'), role='participant', is_accepted=True)
        data = {'code': self.group.invite_code}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("group is full", response.data.get("error", ""))

    def test_join_group_invalid_confirmation(self):
        """
        Test that confirming with an invalid token or confirmation fails
        """
        self.login_as("testuser2")
        url = reverse('group-accept-invitation')
        data = {'confirmation_token': 'invalidtoken'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid confirmation", response.data.get("error", ""))
