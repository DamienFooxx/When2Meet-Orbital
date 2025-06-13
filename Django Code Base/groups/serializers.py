from rest_framework import serializers
from .models import Group, GroupMembership
from accounts.models import Profile
from django.db import transaction

class GroupMembershipListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='profile.user.username')
    name = serializers.CharField(source='profile.name')

    class Meta:
        model = GroupMembership
        fields = ['id', 'username', 'name', 'role', 'joined_at']

class GroupSerializer(serializers.ModelSerializer):
    members = serializers.ListField(
        child=serializers.EmailField(), write_only=True, required=False
    )

    class Meta:
        model = Group
        fields = ['id', 'name', 'members']  # Add other fields if needed

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
            GroupMembership.objects.get_or_create(group=group, profile=profile, role='organiser')

            # Add members by email
            unique_emails = set([email.lower().strip() for email in members_emails])

            for email in members_emails:
                member_profile = Profile.objects.filter(user__email = email).first()

                # skip if not found or is the creator
                if not member_profile or member_profile.id == profile.id:
                    continue

                # avoid duplicate memberships
                GroupMembership.objects.get_or_create(
                    group=group,
                    profile=member_profile,
                    defaults={'role': 'member'}
                )

        return group
