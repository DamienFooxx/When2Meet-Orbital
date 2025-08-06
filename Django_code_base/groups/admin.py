from django.contrib import admin
from .models import Group, GroupMembership

"""
groups/admin.py

Registers Group and GroupMembership models for the Django admin interface.
"""

# Register your models here.

admin.site.register(Group)  # Register Group model
admin.site.register(GroupMembership)  # Register GroupMembership model
