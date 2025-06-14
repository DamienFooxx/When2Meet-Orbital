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
    creator = serializers.ReadOnlyField(source='creator.user.username')
    invite_code = serializers.ReadOnlyField()

    class Meta:
        model = Group
        fields = ['id', 'name', 'invite_code', 'created_at', 'creator', 'members', 'is_organiser']  # Add other fields if needed

    is_organiser = serializers.SerializerMethodField()

    def get_is_organiser(self, group):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            profile = Profile.objects.get(user=request.user)
            return GroupMembership.objects.filter(
                group=group, profile=profile, role='organiser'
            ).exists()
        return False

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
