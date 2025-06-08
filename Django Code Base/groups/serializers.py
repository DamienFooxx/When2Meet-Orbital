from rest_framework import serializers
from .models import Group, GroupMembership
from accounts.models import Profile  # adjust if needed

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

        # Create group and add creator
        group = Group.objects.create(name=validated_data['name'], creator=profile)
        GroupMembership.objects.create(group=group, profile=profile, role='organiser')

        # Add members by email
        for email in members_emails:
            member_profile = Profile.objects.filter(user__email = email).first()

            # skip if not found or is the creator
            if not member_profile or member_profile.id == profile.id:
                continue

            # avoid duplicate memberships
            if not GroupMembership.objects.filter(group=group, profile=member_profile).exists():
                GroupMembership.objects.create(group=group, profile=member_profile, role='member')

            else:
                print(f"[!] Skipped member (duplicate or not found): {email}")
        return group
