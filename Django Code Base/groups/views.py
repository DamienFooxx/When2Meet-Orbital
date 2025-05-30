from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Group, GroupMembership
from .serializers import GroupSerializer, GroupMembershipSerializer

"""
groups/views.py

Contains viewsets for managing groups and group memberships.
"""

# Create your views here.
class GroupViewSet(viewsets.Model.ViewSet):
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

        # Checks if group is full, keeping it low for dev until search algo is efficient enough to allow big groups
        if group.group_memberships.count() >= 10:
            return Response({
                'error' : 'Group is full.'
            }, status = status.HTTP_403_FORBIDDEN)

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




