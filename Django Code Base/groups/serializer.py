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

class GroupMembershipListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='profile.user.username')
    name = serializers.CharField(source='profile.name')

    class Meta:
        model = GroupMembership
        fields = [
            'id', 
            'username', 
            'name', 
            'role', 
            'joined_at'
            ]