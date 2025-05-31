from django.test import TestCase
from django.contrib.auth.models import User
from .models import Group, GroupMembership, Profile
from rest_framework.test import APIClient

# Create your tests here.
class GroupTestCase(TestCase):
    """
    Tests backend
    """
    def setUp(self):
        # Create two users and profiles
        self.user1 = User.objects.create_user(username='damien', password='password')
        self.user2 = User.objects.create_user(username='joanne', password='password')
        self.profile1 = Profile.objects.get(user=self.user1)  # Use auto-created profile
        self.profile1.name = "Damien"
        self.profile2 = Profile.objects.get(user=self.user2)  # Use auto-created profile
        self.profile2.name = "Joanne"
        self.profile1.save()
        self.profile2.save()

        # DRF client, log in as user1 by default
        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)

    def test_create_group(self):
        response = self.client.post('/api/groups/', {'name': 'Test Group'})
        self.assertEqual(response.status_code, 201)
        group = Group.objects.get(name='Test Group')
        # Creator is organiser and member
        membership = GroupMembership.objects.get(group=group, profile=self.profile1)
        self.assertEqual(membership.role, 'organiser')

    def test_join_group_by_code_requires_confirmation(self):
        # User1 creates a group
        group = Group.objects.create(name='Alpha Group', creator=self.profile1)
        GroupMembership.objects.create(group=group, profile=self.profile1, role='organiser')
        invite_code = group.invite_code

        # User2 tries to join (as new client)
        self.client.force_authenticate(user=self.user2)
        response = self.client.post('/api/groups/join-by-code/', {'invite_code': invite_code})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data.get('confirmation_needed'))
        # Not yet a member!
        self.assertFalse(GroupMembership.objects.filter(group=group, profile=self.profile2).exists())

    def test_membership_creation(self):
        # Ensure a group and a profile exist
        group = Group.objects.create(name='Membership Group', creator=self.profile1)
        
        # Simulate user joining group as organiser
        membership = GroupMembership.objects.create(group=group, profile=self.profile1, role='organiser')
        self.assertEqual(membership.role, 'organiser')
        self.assertEqual(membership.profile.user.username, 'damien')

        # Ensure the membership exists in the DB
        self.assertTrue(GroupMembership.objects.filter(group=group, profile=self.profile1, role='organiser').exists())
        
        # Joined date is set
        self.assertIsNotNone(membership.joined_at)

        # Negative check: this profile is not in the group as a participant
        self.assertFalse(GroupMembership.objects.filter(group=group, profile=self.profile1, role='participant').exists())

    def test_confirm_and_join_group_by_code(self):
        group = Group.objects.create(name='Beta Group', creator=self.profile1)
        GroupMembership.objects.create(group=group, profile=self.profile1, role='organiser')
        invite_code = group.invite_code

        self.client.force_authenticate(user=self.user2)
        # Join with confirmation
        response = self.client.post('/api/groups/join-by-code/', {'invite_code': invite_code, 'confirm_join': True})
        self.assertEqual(response.status_code, 201)
        self.assertIn('Successfully joined group', response.data['message'])
        self.assertTrue(GroupMembership.objects.filter(group=group, profile=self.profile2).exists())

    def test_join_group_already_member(self):
        group = Group.objects.create(name='Gamma Group', creator=self.profile1)
        GroupMembership.objects.create(group=group, profile=self.profile1, role='organiser')
        GroupMembership.objects.create(group=group, profile=self.profile2, role='participant')
        invite_code = group.invite_code

        self.client.force_authenticate(user=self.user2)
        response = self.client.post('/api/groups/join-by-code/', {'invite_code': invite_code, 'confirm_join': True})
        self.assertEqual(response.status_code, 200)
        self.assertIn('Already a group member', response.data['error'])

    def test_leave_group_as_participant(self):
        group = Group.objects.create(name='Omega Group', creator=self.profile1)
        GroupMembership.objects.create(group=group, profile=self.profile1, role='organiser')
        GroupMembership.objects.create(group=group, profile=self.profile2, role='participant')

        self.client.force_authenticate(user=self.user2)
        response = self.client.post(f'/api/groups/{group.id}/leave/')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(GroupMembership.objects.filter(group=group, profile=self.profile2).exists())

    def test_leave_group_as_last_member_deletes_group(self):
        group = Group.objects.create(name='Solo Group', creator=self.profile1)
        GroupMembership.objects.create(group=group, profile=self.profile1, role='organiser')

        # Only member tries to leave, first attempt should prompt confirmation
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(f'/api/groups/{group.id}/leave/')
        self.assertEqual(response.status_code, 400)
        self.assertIn('warning', response.data)
        self.assertTrue(Group.objects.filter(id=group.id).exists())

        # Confirm deletion
        response = self.client.post(f'/api/groups/{group.id}/leave/', {'confirm_delete': True})
        self.assertEqual(response.status_code, 200)
        self.assertIn('deleted as you were the last member', response.data['message'])
        self.assertFalse(Group.objects.filter(id=group.id).exists())

    def test_last_organiser_cannot_leave(self):
        group = Group.objects.create(name='Org Group', creator=self.profile1)
        GroupMembership.objects.create(group=group, profile=self.profile1, role='organiser')
        GroupMembership.objects.create(group=group, profile=self.profile2, role='participant')

        self.client.force_authenticate(user=self.user1)
        response = self.client.post(f'/api/groups/{group.id}/leave/')
        self.assertEqual(response.status_code, 403)
        self.assertIn('You are the last organiser', response.data['error'])

    def test_list_members_sorted(self):
        group = Group.objects.create(name='Sorted Group', creator=self.profile1)
        GroupMembership.objects.create(group=group, profile=self.profile1, role='organiser')
        GroupMembership.objects.create(group=group, profile=self.profile2, role='participant')
        # Add more participants
        user3 = User.objects.create_user(username='cathy', password='password')
        profile3 = Profile.objects.get(user=user3)  # Use auto-created profile
        profile3.name = 'Cathy'
        profile3.save()
        GroupMembership.objects.create(group=group, profile=profile3, role='participant')

        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'/api/groups/{group.id}/members/')
        self.assertEqual(response.status_code, 200)
        # Organiser first
        self.assertEqual(response.data[0]['role'], 'organiser')
        # All participants follow, sorted by username
        participant_usernames = [m['username'] for m in response.data if m['role'] == 'participant']
        self.assertEqual(participant_usernames, sorted(participant_usernames))

    def test_group_size_limit(self):
        """
        Ensure a group cannot have more than 10 members.
        """
        group = Group.objects.create(name='Big Group', creator=self.profile1)
        GroupMembership.objects.create(group=group, profile=self.profile1, role='organiser')
        # Add 9 more users (total 10)
        for i in range(2, 11):
            user = User.objects.create_user(username=f'user{i}', password='password')
            profile = Profile.objects.get(user=user)
            profile.name = f'User{i}'
            profile.save()
            GroupMembership.objects.create(group=group, profile=profile, role='participant')
        # 11th user tries to join
        user11 = User.objects.create_user(username='user11', password='password')
        profile11 = Profile.objects.get(user=user11)
        profile11.name = 'User11'
        profile11.save()
        self.client.force_authenticate(user=user11)
        response = self.client.post('/api/groups/join-by-code/', {'invite_code': group.invite_code, 'confirm_join': True})
        self.assertEqual(response.status_code, 403)
        self.assertIn('Group is full', response.data['error'])

    def test_join_group_invalid_invite_code(self):
        """
        Ensure joining with an invalid invite code returns 404.
        """
        self.client.force_authenticate(user=self.user2)
        response = self.client.post('/api/groups/join-by-code/', {'invite_code': 'INVALIDCODE'})
        self.assertEqual(response.status_code, 404)
        self.assertIn('Invalide invite code or Group does not exist', response.data['error'])

    def test_join_group_full_group(self):
        """
        Ensure joining a full group returns 403.
        """
        group = Group.objects.create(name='Full Group', creator=self.profile1)
        GroupMembership.objects.create(group=group, profile=self.profile1, role='organiser')
        # Fill up the group
        for i in range(2, 11):
            user = User.objects.create_user(username=f'fulluser{i}', password='password')
            profile = Profile.objects.get(user=user)
            profile.name = f'FullUser{i}'
            profile.save()
            GroupMembership.objects.create(group=group, profile=profile, role='participant')
        # Another user tries to join
        user12 = User.objects.create_user(username='fulluser12', password='password')
        profile12 = Profile.objects.get(user=user12)
        profile12.name = 'FullUser12'
        profile12.save()
        self.client.force_authenticate(user=user12)
        response = self.client.post('/api/groups/join-by-code/', {'invite_code': group.invite_code, 'confirm_join': True})
        self.assertEqual(response.status_code, 403)
        self.assertIn('Group is full', response.data['error'])

    def test_join_group_invalid_confirmation(self):
        """
        Ensure joining without confirmation returns the correct response.
        """
        group = Group.objects.create(name='Confirm Group', creator=self.profile1)
        GroupMembership.objects.create(group=group, profile=self.profile1, role='organiser')
        invite_code = group.invite_code
        self.client.force_authenticate(user=self.user2)
        # Try to join without confirm_join
        response = self.client.post('/api/groups/join-by-code/', {'invite_code': invite_code})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data.get('confirmation_needed'))
        self.assertIn('Do you want to join the group', response.data['message'])
