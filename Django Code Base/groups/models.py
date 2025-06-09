from django.db import models
import string
import random
from accounts.models import Profile

"""
groups/models.py

Defines Group and GroupMembership models for managing user groups and memberships.
"""

# Create your models here.
def generate_group_code(length = 8):
    """
    Generates a random group invite code consisting of uppercase letters and digits.
    Used for the Group's invite_code field.
    """
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k = length))

class Group(models.Model):
    """
    Represents a user-created group for scheduling events.
    Linked to the Profile model as the creator.
    """
    name = models.CharField(max_length = 100)  # Name of the group
    created_at = models.DateTimeField(auto_now_add = True)  # Timestamp of group creation
    invite_code = models.CharField(max_length = 10, unique = True, default = generate_group_code)  # Unique code for joining
    creator = models.ForeignKey(Profile, on_delete = models.CASCADE, related_name = "created_groups", null = True, blank = True)  # Group creator
    members = models.ManyToManyField(
        'Profile',
        through='GroupMembership',
        related_name='groups'
    )
    
    def __str__(self):
        return self.name
    
    class Meta:
        unique_together = ('creator', 'name')

class GroupMembership(models.Model):
    """
    Represents a user's membership in a group, with a role (organiser or participant).
    Enforces unique membership per user per group.
    """
    ROLE_CHOICES = {
        ('organiser', 'Organiser'),
        ('participant', 'Participant'),
    }

    group = models.ForeignKey(Group, on_delete = models.CASCADE, related_name = 'group_memberships')  # The group this membership belongs to
    profile = models.ForeignKey(Profile, on_delete = models.CASCADE, related_name = 'profile_memberships')  # The user profile in the group
    role = models.CharField(max_length = 20, choices = ROLE_CHOICES, default = 'participant')  # Role in the group
    joined_at = models.DateTimeField(auto_now_add = True)  # When the user joined the group

    class Meta:
        unique_together = ('group', 'profile')  # Ensures a user can only join a group once
    
    def __str__(self):
        return f"{self.profile.user.username} in {self.group.name} ({self.role})"

