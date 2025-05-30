from rest_framework import serializers
from .models import Group, GroupMembership

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = [
            'id',
            'name', 
            'invite_code', 
            'created_at', 
            'creator'
            ]

class GroupMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMembership
        fields = [
            'id',
            'group', 
            'profile', 
            'role', 
            'joined_at'
            ]

