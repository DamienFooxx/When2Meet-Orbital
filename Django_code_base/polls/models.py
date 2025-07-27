from django.db import models
from events.models import Event
from accounts.models import Profile
from availcalendar.models import TimeSlot

class Poll(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="polls"
    )

    def __str__(self):
        return f"Poll for Event {self.event.id}"


class PollOption(models.Model):
    poll = models.ForeignKey(
        Poll, on_delete=models.CASCADE, related_name="options"
    )
    timeslot = models.ForeignKey(
        TimeSlot, on_delete=models.CASCADE, related_name="poll_options"
    )

    def __str__(self):
        return f"Option {self.id} for Poll {self.poll.id}"


class PollVote(models.Model):
    voted_at = models.DateTimeField(auto_now_add=True)
    poll_option = models.ForeignKey(
        PollOption, on_delete=models.CASCADE, related_name="votes"
    )
    voter = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="poll_votes"
    )

    class Meta:
        unique_together = ('poll_option', 'voter')

    def __str__(self):
        return f"{self.voter.user_id} voted for Option {self.poll_option.id}"
