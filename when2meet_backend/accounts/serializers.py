from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Event, TimeSlot

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class TimeSlotSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = TimeSlot
        fields = ['id', 'event', 'user', 'start_time', 'end_time', 'is_available']

class EventSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    participants = UserSerializer(many=True, read_only=True)
    time_slots = TimeSlotSerializer(many=True, read_only=True)
    
    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'created_at', 'start_date', 
                 'end_date', 'creator', 'participants', 'is_active', 'time_slots'] 