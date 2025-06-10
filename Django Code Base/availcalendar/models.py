from django.db import models
from accounts.models import Profile, Location

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
    user = models.ForeignKey(
        'accounts.Profile',
        on_delete = models.CASCADE,
        related_name = "timeslots",
    )
    event = models.ForeignKey(
        Event,
        on_delete = models.CASCADE,
        related_name = "timeslots",
        null = True,
        blank = True,
    )
    start = models.DateTimeField()
    end = models.DateTimeField()
    source = models.CharField(
        max_length = 10,
        choices = (
            ('manual', 'Manual'),
            ('google', 'Google Calendar'),
            ('group', 'Group'),
        ),
        default = 'manual'
    )

    class Meta:
        ordering = ['start']
        unique_together = ('user', 'start', 'end', 'source')

    def clean(self):
        super().clean()
        # 1) Duration must be at least 15 minutes
        duration = self.end - self.start
        if duration < timedelta(minutes = 15):
            raise ValidationError("TimeSlot must be at least 15 minutes long.")

        # 2) (Optional) Align start/end on 15-minute boundaries
        for dt, name in ((self.start, "start"), (self.end, "end")):
            if dt.minute % 15 != 0 or dt.second != 0 or dt.microsecond != 0:
                raise ValidationError({
                    name: f"{name} must be on a 15-minute boundary (e.g. 00, 15, 30, 45)."
                })

    def save(self, *args, **kwargs):
        # run clean() before saving
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.user.username}: {self.start.isoformat()} – {self.end.isoformat()} ({self.source})"