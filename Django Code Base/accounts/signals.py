from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile

"""
accounts/signals.py

Contains signal handlers for creating or updating user profiles when a User is created or saved.
"""

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Signal handler that creates a Profile when a new User is created,
    or updates the Profile when an existing User is saved.
    """
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()
