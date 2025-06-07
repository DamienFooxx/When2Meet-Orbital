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
            try:
                member_profile = Profile.objects.get(user__email=email)
                GroupMembership.objects.create(group=group, profile=member_profile, role='member')
            except Profile.DoesNotExist:
                continue  # skip if no such profile

        return group
