from django.db import models
from accounts.models import Profile, Location
from groups.models import Group
from datetime import timedelta
from django.core.exceptions import ValidationError

class Event(models.Model):
    """
    A table to hold event details
    """
    title = models.CharField(max_length = 50)
    description = models.CharField(max_length = 500, blank = True)
    created_at = models.DateTimeField(auto_now_add = True)
    creator = models.ForeignKey(
        'accounts.Profile',
        on_delete = models.CASCADE,
        related_name = "created_events",
    )
    location_id = models.ForeignKey(
        'accounts.Location',
        on_delete = models.SET_NULL,
        null = True,
        blank = True,
        related_name = "events",
    )
    group = models.ForeignKey(
        'groups.Group',
        on_delete = models.CASCADE,
        related_name = "events",
        null = True
    )
    participants = models.ManyToManyField(
        'accounts.Profile',
        related_name = "events",
    )

    def __str__(self):
        return self.title

class TimeSlot(models.Model):
    """
    A model to store timeslots in the database
    """
    event_id = models.ForeignKey(
        Event,
        on_delete = models.CASCADE,
        related_name = "timeslots",
        null = True,
        blank = True,
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(
        max_length = 20,
        choices = [('not confirmed', 'Not Confirmed'), ('confirmed', 'Confirmed')],
        default = 'not confirmed'
    )

    class Meta:
        ordering = ['start_time']
        unique_together = ('event_id', 'start_time', 'end_time', 'status')

    def clean(self):
        super().clean()
        # 1) Duration must be at least 15 minutes
        duration = self.end_time - self.start_time
        if duration < timedelta(minutes = 15):
            raise ValidationError("TimeSlot must be at least 15 minutes long.")

        # 2) (Optional) Align start/end on 15-minute boundaries
        for dt, name in ((self.start_time, "start_time"), (self.end_time, "end_time")):
            if dt.minute % 15 != 0 or dt.second != 0 or dt.microsecond != 0:
                raise ValidationError({
                    name: f"{name} must be on a 15-minute boundary (e.g. 00, 15, 30, 45)."
                })

    def save(self, *args, **kwargs):
        # run clean() before saving
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.created_by.user.username}: {self.start_time.isoformat()} – {self.end_time.isoformat()} ({self.status})"

class CalendarEntry(models.Model):
    """
    A model to store availabilities of users, it can store by the following methods
        - A manually inputted event
        - An added event from a group
        - Events synced in via Google Calendar
    """
    title = models.CharField(max_length = 100)
    description = models.CharField(max_length = 500, blank = True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add = True, editable = False)
    updated_at = models.DateTimeField(auto_now_add = True)
    source = models.CharField(
        max_length = 10,
        choices = [
            ('manual', 'Manual'),
            ('google', 'Google Calendar'),
            ('group', 'Group'),
        ],
        default = 'manual'
    )
    google_event_id = models.CharField(max_length = 50, null = True)
    location_id = models.ForeignKey(
        'accounts.Location',
        on_delete = models.SET_NULL,
        null = True,
        blank = True,
        related_name = "CalendarEntry",
    )
    user_id = models.ForeignKey(
        'accounts.Profile',
        related_name = "CalendarEntry",
        on_delete = models.CASCADE,
    )
    event_id = models.ForeignKey(
        Event,
        on_delete = models.CASCADE,
        related_name = "CalendarEntry"
    )

    def __str__(self):
        return self.title

class CalendarIntegration(models.Model):
    """
    This is a model to store the essential tokens for Google Calendar sync with user accounts
    """
    provider = models.CharField(
        max_length = 10,
        choices = [('google', 'Google')],
        default = 'google',
    )
    # Google’s unique user ID (the “sub” claim in their ID token)
    external_id = models.CharField(
        max_length = 255,
        help_text = "Google user ID (sub)"
    )
    # Short-lived access token for Calendar API calls
    access_token = models.TextField(
        help_text = "OAuth2 access token"
    )
    # Long-lived refresh token (only provided on first consent)
    refresh_token = models.TextField(
        null = True,
        blank = True,
        help_text = "OAuth2 refresh token"
    )
    # When the access_token expires next (UTC)
    token_expiry = models.DateTimeField(
        help_text = "UTC datetime when access_token expires"
    )
    # Link back to your Profile model
    user = models.ForeignKey(
        Profile,
        on_delete = models.CASCADE,
        related_name = "calendar_integrations"
    )
    
    class Meta:
        unique_together = ('provider', 'user')
        verbose_name = "Calendar Integration"
        verbose_name_plural = "Calendar Integrations"

    def __str__(self):
        return f"{self.user_id.user.username}'s {self.provider} Calendar Integration"

class ManualAvailability(models.Model):
    """
    This is a model to store the manually inputed availabilities of user on the in app calendar
    """
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    recurrence = models.CharField(
        max_length=200,
        blank=True,
        help_text='RRULE string for recurrence (e.g. "FREQ=DAILY;INTERVAL=1")'
    )
    user = models.ForeignKey(
        'accounts.Profile',
        on_delete = models.CASCADE,
        related_name = "ManualAvailability"
    )

    class Meta:
        ordering = ['start_time']
        verbose_name = 'Manual Availability'
        verbose_name_plural = 'Manual Availabilities'

    def clean(self):
        super().clean()
        # end must be after start
        if self.end_time <= self.start_time:
            raise ValidationError("`end_time` must be after `start_time`.")
        # enforce 15-minute minimum
        if (self.end_time - self.start_time) < timedelta(minutes=15):
            raise ValidationError("Intervals must be at least 15 minutes long.")

    def save(self, *args, **kwargs):
        # run our clean() before saving
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.start_time} to {self.end_time}"

class Reminder(models.Model):
    """
    This is a model to store reminders for in app notifications about events
    """
    remind_at = models.DateTimeField()
    calendar_entry_id = models.ForeignKey(
        CalendarEntry,
        on_delete = models.CASCADE,
        related_name = "reminders"
    )
    user_id = models.ForeignKey(
        'accounts.Profile',
        on_delete = models.CASCADE,
        related_name = "reminders"
    )

    def __str__(self):
        return self.calendar_entry_id.title