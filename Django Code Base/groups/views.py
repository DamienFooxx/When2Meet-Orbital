from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Group, GroupMembership
from .serializers import GroupSerializer
from accounts.models import Profile

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


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("Serializer errors:", serializer.errors)
            return Response(serializer.errors, status = 400)
        self.perform_create(serializer)
        return Response(serializer.data, status=201)


