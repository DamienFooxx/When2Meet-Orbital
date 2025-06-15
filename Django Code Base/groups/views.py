from django.db import models
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
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
        serializer.save(creator = profile)

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
                'error': 'Invalid invite code or Group does not exist.'
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

        # Add User as member
        GroupMembership.objects.create(
            group = group,
            profile = profile,
            role = 'member',
            is_accepted = True
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
        try:
            print("Fetching group:", pk)
            group = self.get_object()
            print("Group fetched:", group.name)


            memberships = group.group_memberships.select_related('profile__user').all()
            print("Memberships found:", memberships.count())
            
            # Ordered by role, organisers first, then join by username alphabetically
            memberships = memberships.order_by(
                models.Case(
                    models.When(role = 'organiser', then = 0),
                    models.When(role = 'member', then = 1),
                    output_field = models.IntegerField(),
                ),
                'profile__user__username'
            )
            serializer = GroupMembershipListSerializer(memberships, many = True)
            return Response(serializer.data)
        except Exception as e:
            print("Error in list_members:", e)
            return Response({"error": str(e)}, status=500)
    
    @action(detail=False, methods=['get'], url_path='invitations', permission_classes=[IsAuthenticated])
    def invitations(self, request):
        profile = Profile.objects.get(user=request.user)

        memberships = GroupMembership.objects.filter(
            profile=profile,
            is_accepted=False
        ).select_related('group')

        groups = [membership.group for membership in memberships]
        serializer = GroupSerializer(groups, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='accept-invitation')
    def accept_invitation(self, request, pk=None):
        group = self.get_object()

        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            return Response({'error': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        membership = GroupMembership.objects.filter(
            group=group, profile=profile, is_accepted=False
        ).first()

        if not membership:
            return Response({'error': 'No pending invitations.'}, status=status.HTTP_400_BAD_REQUEST)
        
        membership.is_accepted = True
        membership.save()

        return Response({'message': f'You have joined the group "{group.name}".'}, status=status.HTTP_200_OK)
       
    @action(detail=True, methods=['post'], url_path='decline-invitation')
    def decline_invitation(self, request, pk=None):
        group = self.get_object()
        profile = Profile.objects.get(user=request.user)

        membership = GroupMembership.objects.filter(
            group=group,
            profile=profile,
            is_accepted=False
        ).first()

        if not membership:
            return Response({'error': 'No pending invitation to decline'}, status=status.HTTP_400_BAD_REQUEST)
        
        membership.delete()

        return Response({'message': f'You have declined the invitation to join "{group.name}".'}, status=status.HTTP_200_OK)
    
    def list(self, request, *args, **kwargs):
        profile = Profile.objects.get(user=request.user)
        queryset = Group.objects.filter(
            group_memberships__profile=profile,
            group_memberships__is_accepted=True
        ).distinct()
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        group = self.get_object()
        profile = Profile.objects.get(user=request.user)

        # only allow organisers to delete the group
        if not GroupMembership.objects.filter(group=group, profile=profile, role='organiser').exists():
            return Response({'error': 'Only organisers can delete the group.'},
                            status=status.HTTP_403_FORBIDDEN)
        
        group.delete()
        return Response({'message': 'Group deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


