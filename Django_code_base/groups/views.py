from django.db import models
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from accounts.models import Profile
from .models import Group, GroupMembership
from .serializers import (
    GroupSerializer,
    GroupMembershipListSerializer,
    GroupInvitationSerializer,
)
from django.contrib.auth import get_user_model

"""
groups/views.py

Contains viewsets for managing groups and group memberships.
"""
User = get_user_model()


# Create your views here.
class GroupViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing, creating, and managing groups.
    Only authenticated users can access these endpoints.
    """

    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    # --- Membership Management ---
    def perform_create(self, serializer):
        user = self.request.user
        profile = Profile.objects.get(user=user)
        serializer.save(creator=profile)

    def destroy(self, request, *args, **kwargs):
        group = self.get_object()
        profile = Profile.objects.get(user=request.user)
        if not GroupMembership.objects.filter(group=group, profile=profile, role="organiser").exists():
            return Response({"error": "Only organisers can delete the group."}, status=status.HTTP_403_FORBIDDEN)
        group.delete()
        return Response({"message": "Group deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["get"], url_path="members")
    def list_members(self, request, pk=None):
        """
        Lists all group members, organisers appear at the top
        """
        try:
            group = self.get_object()
            memberships = group.group_memberships.select_related("profile__user").all()

            # Ordered by role, organisers first, then join by username alphabetically
            memberships = memberships.order_by(
                models.Case(
                    models.When(role="organiser", then=0),
                    models.When(role="member", then=1),
                    output_field=models.IntegerField(),
                ),
                "profile__user__username",
            )
            serializer = GroupMembershipListSerializer(memberships, many=True)
            return Response(serializer.data)
        except Exception as e:
            print("Error in list_members:", e)
            return Response({"error": str(e)}, status=500)

    @action(detail=True, methods=["post"], url_path="leave")
    def leave_group(self, request, pk=None):
        """
        Allows users to leave the group
        If they are the last member, prompt for confirmation before deleting the group.
        Prevents last organiser from leaving without assigning another organiser.
        """
        group = self.get_object()
        profile = Profile.objects.get(user=request.user)
        membership = GroupMembership.objects.filter(group=group, profile=profile).first()

        if not membership:
            return Response({"error": "Not a member of the group."}, status=status.HTTP_400_BAD_REQUEST)

        if membership.role == "organiser":
            organiser_count = GroupMembership.objects.filter(group=group, role="organiser").count()
            # Checks if person leaving is the last organiser left in the group
            if organiser_count == 1 and group.group_memberships.count() > 1:
                return Response({"error": "You are the last organiser of the group. Assign another member as an organiser before leaving."}, status=status.HTTP_403_FORBIDDEN)

        member_count = GroupMembership.objects.filter(group=group).count()

        if member_count == 1:
            # If confirmed
            group.delete()
            return Response({"message": f'Group "{group.name}" deleted as you were the last member.'}, status=status.HTTP_200_OK)

        membership.delete()
        return Response({"message": f'You have left the group "{group.name}".'}, status=status.HTTP_200_OK)

    # --- Invitations and Requests ---
    @action(detail=False, methods=["get"], url_path="invitations")
    def invitations(self, request):
        profile = Profile.objects.get(user=request.user)
        memberships = GroupMembership.objects.filter(profile=profile, is_accepted=False, invited_by_organizer=True).select_related("group", "group_creator")
        serializer = GroupInvitationSerializer(memberships, many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="invite")
    def invite_users(self, request, pk=None):
        """
        Invite one or more users to a group using email addresses.
        Accepts 'identifier' (string) or 'identifiers' (list).
        """
        group = self.get_object()
        profile = Profile.objects.get(user=request.user)

        # Check if the user is an organiser
        if not group.group_memberships.filter(profile=profile, role="organiser", is_accepted=True).exists():
            return Response({"error": "Only organisers can invite users."}, status=status.HTTP_403_FORBIDDEN)

        identifiers = request.data.get("identifier") or request.data.get("identifiers")

        if not identifiers:
            return Response({"error": "No email(s) provided."}, status=status.HTTP_400_BAD_REQUEST)

        if isinstance(identifiers, str):
            identifiers = [identifiers]

        invited, already_members, not_found = [], [], []
        for email in identifiers:
            email = email.strip().lower()
            try:
                user = User.objects.get(email__iexact=email)
                target_profile = Profile.objects.get(user=user)
            except (User.DoesNotExist, Profile.DoesNotExist):
                not_found.append(email)
                continue
            if group.group_memberships.filter(profile=target_profile).exists():
                already_members.append(email)
                continue
            group.group_memberships.create(profile=target_profile, role="member", is_accepted=False, invited_by_organizer=True)
            invited.append(email)
        return Response({"message": f"{len(invited)} invited, {len(already_members)} already in group, {len(not_found)} not found.", "invited": invited, "already_members": already_members, "not_found": not_found}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="join-by-code")
    def join_by_code(self, request):
        """
        Allows users to join the group via the invite code
        """
        code = request.data.get("invite_code")

        if not code:
            return Response({"error": "Invite code is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            group = Group.objects.get(invite_code=code)
        except Group.DoesNotExist:
            return Response({"error": "Invalid invite code or Group does not exist."}, status=status.HTTP_404_NOT_FOUND)

        profile = Profile.objects.get(user=request.user)

        # Checks if User is already in the Group
        if GroupMembership.objects.filter(group=group, profile=profile, is_accepted=True).exists():
            return Response({"error": "Already a group member."}, status=status.HTTP_200_OK)

        # Check if the User has already sent a request to join
        if GroupMembership.objects.filter(group=group, profile=profile, is_accepted=False).exists():
            return Response({"error": "You have already sent a join request to this group. Please wait for the organizer to approve your request."}, status=status.HTTP_200_OK)

        # Checks if group is full, keeping it low for now until search algo is efficient enough to allow big groups
        if group.group_memberships.count() >= group.max_size:
            return Response({"error": "Group is full."}, status=status.HTTP_403_FORBIDDEN)

        # Ask user for confirmation beforre sending the join request
        confirm = request.data.get("confirm_join")
        if not confirm:
            return Response({"confirmation_needed": True, "group_name": group.name, "message": f'Do you want to request to join the group "{group.name}"?', "group_info": {"name": group.name, "invite_code": group.invite_code}}, status=status.HTTP_200_OK)

        # Create a pending group membership (requesting to join)
        GroupMembership.objects.create(group=group, profile=profile, role="member", is_accepted=False, invited_by_organizer=False)

        return Response({"message": f'Your request to join group "{group.name}" has been sent to organizer.', "group_name": group.name}, status=status.HTTP_201_CREATED)

    # --- Accept/Decline Invitation ---
    @action(detail=True, methods=["post"], url_path="accept-invitation")
    def accept_invitation(self, request, pk=None):
        try:
            membership = GroupMembership.objects.get(id=pk, is_accepted=False)
        except GroupMembership.DoesNotExist:
            return Response({"error": "No pending invitations."}, status=status.HTTP_404_NOT_FOUND)
        if membership.profile.user != request.user:
            return Response({"error": "You are not authorized to accept this invitation."}, status=status.HTTP_403_FORBIDDEN)
        membership.is_accepted = True
        membership.save()
        return Response({"message": f'You have joined the group "{membership.group.name}".'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="decline-invitation")
    def decline_invitation(self, request, pk=None):
        try:
            membership = GroupMembership.objects.get(id=pk, is_accepted=False)
        except GroupMembership.DoesNotExist:
            return Response({"error": "No pending invitation to decline"}, status=status.HTTP_404_NOT_FOUND)
        if membership.profile.user != request.user:
            return Response({"error": "You are not authorized to decline this invitation."}, status=status.HTTP_403_FORBIDDEN)
        group_name = membership.group.name
        membership.delete()
        return Response({"message": f'You have declined the invitation to join "{group_name}".'}, status=status.HTTP_200_OK)

    # --- Accept/Decline Join Request ---
    @action(detail=False, methods=["post"], url_path="requests/(?P<pk>[^/.]+)/accept-request", permission_classes=[IsAuthenticated])
    def accept_join_request(self, request, pk=None):
        try:
            membership = GroupMembership.objects.select_related("group", "profile").get(id=pk, is_accepted=False, invited_by_organizer=False)
            organizer_profile = Profile.objects.get(user=request.user)
            is_organiser = GroupMembership.objects.filter(group=membership.group, profile=organizer_profile, role="organiser").exists()
            if not is_organiser:
                return Response({"error": "Only organisers can accept join requests."}, status=status.HTTP_403_FORBIDDEN)
            membership.is_accepted = True
            membership.save()
            return Response({"message": f"User {membership.profile.user.username} has been added to the group '{membership.group.name}'."}, status=status.HTTP_200_OK)
        except GroupMembership.DoesNotExist:
            return Response({"error": "Join request not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=["post"], url_path="requests/(?P<pk>[^/.]+)/decline-request", permission_classes=[IsAuthenticated])
    def decline_join_request(self, request, pk=None):
        try:
            membership = GroupMembership.objects.select_related("group", "profile").get(id=pk, is_accepted=False, invited_by_organizer=False)
            organizer_profile = Profile.objects.get(user=request.user)
            if not GroupMembership.objects.filter(group=membership.group, profile=organizer_profile, role="organiser").exists():
                return Response({"error": "Only organisers can decline join requests."}, status=status.HTTP_403_FORBIDDEN)
            membership.delete()
            return Response({"message": f"Join request for user {membership.profile.user.username} to group '{membership.group.name}' has been declined."}, status=status.HTTP_200_OK)
        except GroupMembership.DoesNotExist:
            return Response({"error": "Join request not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
