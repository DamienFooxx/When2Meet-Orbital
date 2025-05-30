from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Group, GroupMembership
from .serializers import GroupSerializer, GroupMembershipSerializer

"""
groups/views.py

Contains viewsets for managing groups and group memberships.
"""

# Create your views here.
class GroupViewSet(viewserts.Model.ViewSet):
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


