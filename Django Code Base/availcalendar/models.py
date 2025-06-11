from django.db import models
from accounts.models import Profile, Location
from datetime import timedelta
from django.core.exceptions import ValidationError

class Event(models.Model):
    """
    A table to hold event details
    """
    title = models.CharField(max_length=50)
    description = models.CharField(max_length = 500, blank = True)
    location = models.ForeignKey(
        'accounts.Location',
        on_delete = models.SET_NULL,
        null = True,
        blank = True,
       related_name = "events",
    )
    creator = models.ForeignKey(
        'accounts.Profile',
        on_delete = models.CASCADE,
        related_name = "created_events",
    )
    participants = models.ManyToManyField(
        'accounts.Profile',
        related_name = "events",
    )
    created_at = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return self.title

class TimeSlot(models.Model):
    """
    A model to store availabilities of users, it can store by the following methods
        - A manually inputted event
        - An added event from a group
        - Events synced in via Google Calendar
    """
    created_by = models.ForeignKey(
        'accounts.Profile',
        on_delete = models.CASCADE,
        related_name = "timeslots",
    )
    eventid = models.ForeignKey(
        Event,
        on_delete = models.CASCADE,
        related_name = "timeslots",
        null = True,
        blank = True,
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    source = models.CharField(
        max_length = 10,
        choices = (
            ('manual', 'Manual'),
            ('google', 'Google Calendar'),
            ('group', 'Group'),
        ),
        default = 'manual'
    )
    is_confirmed = models.BooleanField(default = False)

    class Meta:
        ordering = ['start_time']
        unique_together = ('created_by', 'start_time', 'end_time', 'source')

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
        return f"{self.created_by.user.username}: {self.start_time.isoformat()} – {self.end_time.isoformat()} ({self.source})"