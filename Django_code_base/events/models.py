from django.db import models
from accounts.models import Profile, Location
from groups.models import Group


class Event(models.Model):
    """
    A table to hold event details
    """
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('collecting_availability', 'Collecting Availability'),
        ('polling', 'Polling'),
        ('confirmed', 'Confirmed'),
    ]

    title = models.CharField(max_length=50)
    description = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(
        "accounts.Profile",
        on_delete=models.CASCADE,
        related_name="created_events",
    )
    location_id = models.ForeignKey(
        "accounts.Location",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
    )
    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.CASCADE,
        related_name="events",
        null=True
    )
    participants = models.ManyToManyField(
        "accounts.Profile",
        through="EventParticipant",
        related_name="events",
    )
    confirmed_timeslot = models.ForeignKey(
        'availcalendar.TimeSlot',
        on_delete = models.SET_NULL,
        related_name = "timeslots",
        null=True,
        blank=True,
    )
    
    # Workflow fields
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='draft')
    availability_start_date = models.DateField(null=True, blank=True)
    availability_end_date = models.DateField(null=True, blank=True)
    availability_start_time = models.TimeField(null=True, blank=True)
    availability_end_time = models.TimeField(null=True, blank=True)
    duration_minutes = models.IntegerField(null=True, blank=True, help_text="Event duration in minutes")

    class Meta:
        db_table = "availcalendar_event"

    def __str__(self):
        return self.title


class EventParticipant(models.Model):
    """
    Many to Many model between Event and Profile to store participation details.
    """
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    participant = models.ForeignKey('accounts.Profile', on_delete=models.CASCADE)
    is_joining = models.CharField(
        max_length=10, 
        choices=[
            ('going', 'Going'), 
            ('maybe', 'Maybe'), 
            ('declined', 'Declined')
            ], null=True, 
            blank=True
        )

    class Meta:
        db_table = "availcalendar_eventparticipant"
        unique_together = ("event", "participant")

    def __str__(self):
        return f"{self.participant.user.username} in {self.event.title}"
