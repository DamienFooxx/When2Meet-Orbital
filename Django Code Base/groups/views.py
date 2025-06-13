from django.shortcuts import render
from django.db import models
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from accounts.models import Profile
from .models import Group, GroupMembership
from .serializers import GroupSerializer, GroupMembershipListSerializer

"""
groups/views.py

Contains viewsets for managing groups and group memberships.
"""

# Create your views here.
class GroupViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing, creating, and managing groups.
    Only authenticated users can access these endpoints.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """
        Creates a new group and sets the requesting user as the creator and organiser.
        Automatically creates a GroupMembership for the creator.
        """
        user = self.request.user
        profile = Profile.objects.get(user = user)
        # Save the group and set creator
        group = serializer.save(creator = profile)

        #Create membership to set creator as organiser by default automatically
        GroupMembership.objects.create(
            group = group,
            profile = profile,
            role = 'organiser'
        )

    @action(detail = False, methods = ['post'], url_path = 'join-by-code')
    def join_by_code(self, request):
        """
        Allows users to join the group via the invite code
        """
        code = request.data.get('invite_code')
        
        # If user does not enter a code
        if not code:
            return Response({
                'error': 'Invite code is required.'
            }, status = status.HTTP_400_BAD_REQUEST)
        try:
            group = Group.objects.get(invite_code = code)
        
        # Checks if the Group with that invite code exists
        except Group.DoesNotExist:
            return Response({
                'error': 'Invalide invite code or Group does not exist.'
            }, status = status.HTTP_404_NOT_FOUND)

        profile = Profile.objects.get(user = request.user)
        
        # Checks if User is already in the Group
        if GroupMembership.objects.filter(group = group, profile = profile).exists():
            return Response({
                'error' : 'Already a group member.'
            }, status = status.HTTP_200_OK)

        # Checks if group is full, keeping it low for now until search algo is efficient enough to allow big groups
        if group.group_memberships.count() >= 10:
            return Response({
                'error' : 'Group is full.'
            }, status = status.HTTP_403_FORBIDDEN)

        # Ask user for confirmation first before joining
        confirm = request.data.get('confirm_join')
        if not confirm:
            return Response({
                'confirmation_needed': True,
                'group_name': group.name,
                'message': f'Do you want to join the group "{group.name}"?',
                'group_info': {
                    'name': group.name,
                }
            }, status=status.HTTP_200_OK)

        # Add User as participant
        GroupMembership.objects.create(
            group = group,
            profile = profile,
            role = 'participant'
        )

        return Response({
            'message' : f'Successfully joined group "{group.name}".',
            'group_name' : group.name
        }, status = status.HTTP_201_CREATED)

    @action(detail = True, methods = ['post'], url_path = 'leave')
    def leave_group(self, request, pk = None):
        """
        Allows users to leave the group
        If they are the last member, prompt for confirmation before deleting the group.
        Prevents last organiser from leaving without assigning another organiser.
        """
        group = self.get_object()
        profile = Profile.objects.get(user = request.user)
        membership = GroupMembership.objects.filter(group = group, profile = profile).first()
        
        if not membership:
            return Response({
                'error' : 'Not a member of the group.'
            }, status = status.HTTP_400_BAD_REQUEST)
        
        member_count = GroupMembership.objects.filter(group = group).count()

        # Automatically delete Group if there are no members left
        if member_count == 1:
            # Confirmation message
            confirm = request.data.get('confirm_delete', False)
            if not confirm:
                return Response({
                    'warning' : f'You are the last member of "{group.name}". Leaving the group will cause the group to be deleted. Confirm by sending {{"confirm_delete": true}} in your request.'
                }, status = status.HTTP_400_BAD_REQUEST)
            # If confirmed
            group.delete()
            return Response({
                'message': f'Group "{group.name}" deleted as you were the last member.'
            }, status = status.HTTP_200_OK)

        # Checks if they are the last organiser
        if membership.role == 'organiser':
            organiser_count = GroupMembership.objects.filter(group = group, role = 'organiser').count()
            # Checks if person leaving is the last organiser left in the group
            if organiser_count == 1:
                return Response({
                    'error' : 'You are the last organiser of the group. Assign another member as an organiser before leaving.'
                }, status = status.HTTP_403_FORBIDDEN)

        # Let the user leave the group
        membership.delete()
        return Response({
            'message': f'You have left the group "{group.name}".'
        }, status=status.HTTP_200_OK)

    @action(detail = True, methods = ['get'], url_path = 'members')
    def list_members(self, request, pk = None):
        """
        Lists all group members, organisers appear at the top
        """
        group = self.get_object()
        memberships = group.group_memberships.select_related('profile__user').all()

        # Ordered by role, organisers first, then join by username alphabetically
        memberships = memberships.order_by(
            models.Case(
                models.When(role = 'organiser', then = 0),
                models.When(role = 'participant', then = 1),
                output_field = models.IntegerField(),
            ),
            'profile__user__username'
        )
        serializer = GroupMembershipListSerializer(memberships, many = True)
        return Response(serializer.data)


