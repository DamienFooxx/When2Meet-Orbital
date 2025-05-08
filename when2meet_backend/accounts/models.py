from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=1000, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_events')
    participants = models.ManyToManyField(User, related_name='participating_events', blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=['creator']),
            models.Index(fields=['start_date']),
            models.Index(fields=['end_date']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.title

class TimeSlot(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='time_slots')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='time_slots')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_available = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=['event']),
            models.Index(fields=['user']),
            models.Index(fields=['start_time']),
            models.Index(fields=['end_time']),
        ]

    def __str__(self):
        return f"{self.event.title} - {self.user.username} ({self.start_time} to {self.end_time})"
