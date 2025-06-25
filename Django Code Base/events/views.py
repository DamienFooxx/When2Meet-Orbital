from django.shortcuts import render
from django.db.models import Q
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from events.models import Event
from events.serializers import EventSerializer
from groups.models import GroupMembership

# Create your views here.

class EventViewSet(viewsets.ModelViewSet):
    """
    CRUD for calendar Events. Only events the user created or participates in.
    """
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        profile = self.request.user.profile
        return Event.objects.filter(
            Q(participants = profile) | Q(creator = profile)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(creator = self.request.user.profile)

    def destroy(self, request, *args, **kwargs):
        event = self.get_object()
        user_profile = request.user.profile
        # If event is linked to a group, check organiser role
        if event.group:
            is_organiser = GroupMembership.objects.filter(
                group = event.group,
                profile = user_profile,
                role = 'organiser',
                is_accepted = True
            ).exists()
            if not is_organiser:
                return Response({'detail': 'Only organisers can delete events from the group.'}, status = status.HTTP_403_FORBIDDEN)
        else:
            # If not a group event, only creator can delete
            if event.creator != user_profile:
                return Response({'detail': 'Only the creator can delete this event.'}, status = status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)
