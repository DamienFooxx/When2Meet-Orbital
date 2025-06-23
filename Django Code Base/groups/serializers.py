from rest_framework import serializers
from .models import Group, GroupMembership, Profile
from accounts.models import Profile
from django.db import transaction
from accounts.serializers import ProfileSerializer

class GroupMembershipListSerializer(serializers.ModelSerializer):
    """
    Serializer for GroupMembership that includes the profile data.
    """
    profile = serializers.SerializerMethodField()
    is_accepted = serializers.BooleanField()

    class Meta:
        model = GroupMembership
        fields = ['id', 'profile', 'role', 'joined_at', 'is_accepted']

    def get_profile(self, obj):
        return ProfileSerializer(obj.profile, context=self.context).data

class GroupSerializer(serializers.ModelSerializer):
    creator = serializers.ReadOnlyField(source='creator.user.username')
    invite_code = serializers.ReadOnlyField()
    is_organiser = serializers.SerializerMethodField()
    members = serializers.SerializerMethodField()  # Add this line

    class Meta: 
        model = Group
        fields = ['id', 'name', 'invite_code', 'created_at', 'creator', 'is_organiser', 'members']

    def get_is_organiser(self, group):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            profile = Profile.objects.get(user=request.user)
            return GroupMembership.objects.filter(
                group=group, profile=profile, role='organiser'
            ).exists()
        return False

    def get_members(self, group):
        memberships = group.group_memberships.select_related('profile__user').all()
        return GroupMembershipListSerializer(memberships, many=True, context=self.context).data

    def create(self, validated_data):
        members_emails = validated_data.pop('members', [])
        request = self.context['request']
        user = request.user
        profile = Profile.objects.get(user=user)
        
        # prevents duplicate group names before creating
        if Group.objects.filter(name=validated_data['name'], creator=profile).exists():
            raise serializers.ValidationError("You already have a group with this name.")
        
        with transaction.atomic():
        # Create group and add creator       
            group = Group.objects.create(name=validated_data['name'], creator=profile)
            
            # add creator as organiser
            GroupMembership.objects.get_or_create(
                group=group, 
                profile=profile, 
                role='organiser', 
                is_accepted=True
            )
            print("Organiser added.")

            unique_emails = set(
                email.lower().strip()
                for email in members_emails 
                if email and email.strip()
            )
            print("Inviting members:", unique_emails)

            for email in unique_emails:
                try:
                    print("Inviting:", email)
                    member_profile = Profile.objects.get(user__email=email)
                    if member_profile == profile:
                        print("Skipping organiser email.")
                        continue

                    GroupMembership.objects.get_or_create(
                        group=group,
                        profile=member_profile,
                        defaults={
                            'role': 'member', 
                            'is_accepted': False
                        }
                    )
                    print("Member added:", email)
                except Profile.DoesNotExist:
                    print("User with email not found:", email)
                    continue
                except Exception as e:
                    print("ERROR inviting", email, ":", str(e))
                    raise e
        return group
