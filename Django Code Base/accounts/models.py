from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField
from localflavor.sg.models import SGPostalCodeField
from geopy.geocoders import GoogleV3
import string
import random

geolocator = GoogleV3(api_key=os.getenv('GOOGLE_MAPS_API_KEY'))

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
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_id = models.CharField(
        max_length = 8,
        unique = True,
        default = generate_unique_id,
        editable = False  # Prevents manual editing in admin
    )
    name = models.CharField(max_length=100, blank = True)
    google_id = models.CharField(max_length=100, blank = True, null = True)
    date_joined = models.DateTimeField(auto_now_add=True)
    country = CountryField(blank_label='(select country)', default='SG')
    state = models.CharField(max_length=100, blank=True, null=True)
    street_address = models.CharField(max_length=255, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name or self.user.email
