from django.db import models
from django.contrib.auth.models import User
import string
import random

def generate_unique_id(length = 8):
    """
    Generates a random unique ID consisting of letters and digits.
    Used for the Profile's unique_id field.
    """
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k = length))

# Create your models here.
class Profile(models.Model):
    """
    Extends the default Django User model with additional fields for the When2Meet app.
    """
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    name = models.CharField(max_length = 100, blank = True)  # User's display name
    location = models.CharField(max_length = 255, blank = True)  # User's location (future: Google Maps integration)
    unique_id = models.CharField(
        max_length = 8,
        unique = True,
        default = generate_unique_id,
        editable = False  # Prevents manual editing in admin
    )

    def __str__(self):
        return f"{self.user.username}'s profile"
