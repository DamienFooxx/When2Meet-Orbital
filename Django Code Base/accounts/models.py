from django.db import models
from django.contrib.auth.models import User
import string
import random

def generate_unique_id(length = 8):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k = length))

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    name = models.CharField(max_length = 100, blank = True)
    location = models.CharField(max_length = 255, blank = True) # Add in Google Maps linked functionality later on
    unique_id = models.CharField(
        max_length = 8,
        unique = True,
        default = generate_unique_id,
        editable = False
    )

    def __str__(self):
        return f"{self.user.username}'s profile"
