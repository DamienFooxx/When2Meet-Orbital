from django.db import models
from django.contrib.auth import get_user_model
from django_countries.fields import CountryField
from django.core.exceptions import ValidationError
from geopy.geocoders import GoogleV3
import string
import random
import os

User = get_user_model()

geolocator = GoogleV3(api_key=os.getenv('GOOGLE_MAPS_API_KEY'))

class Location(models.Model):
    '''
    A model to encapsulate Location Data to be used by other models
    '''
    postalcode = models.CharField(max_length = 50)
    city = models.CharField(max_length = 50, null = True, default = 'Singapore')
    country = CountryField(blank_label='(select country)', default='SG')
    street_address = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def clean(self):
        """
        Verify the address by geocoding via Google Maps.
        If no match, raise ValidationError.
        Otherwise, store latitude and longitude.
        """
        # build full address string
        components = filter(None, [
            self.street_address,
            self.postalcode,
            self.city,
            self.country.name
                  ])
        full_address = ", ".join(components)

        # ask Google to geocode
        location = geolocator.geocode(full_address)
        if location is None:
            raise ValidationError("Address not found: please enter a valid street/postal code.")  

        # store the coords
        self.latitude  = location.latitude
        self.longitude = location.longitude

    def save(self, *args, **kwargs):
        # this runs clean() and raises if validation fails
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.postalcode or self.street_address

def generate_unique_id(length = 8):
    """
    Generates a random unique ID consisting of letters and digits.
    Used for the Profile's unique_id field.
    """
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k = length))

class Profile(models.Model):
    """
    Extends the default Django User model with additional fields for the When2Meet app.
    """
    user = models.OneToOneField(
        User,
        on_delete = models.CASCADE,
        related_name = "profile"
    )
    unique_id = models.CharField(
        max_length = 8,
        unique = True,
        default = generate_unique_id,
        editable = False,  # Prevents manual editing in admin
        primary_key = True
    )
    name = models.CharField(max_length = 100, blank = True)
    google_id = models.CharField(max_length = 100, blank = True, null = True)
    date_joined = models.DateTimeField(auto_now_add = True)
    location = models.ForeignKey(
        Location,
        on_delete = models.SET_NULL,
        null = True,
        blank = True,
        related_name = "profiles"
    )

    def __str__(self):
        return self.name or self.user.email