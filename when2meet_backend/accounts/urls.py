from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'events', views.EventViewSet, basename='event')
router.register(r'timeslots', views.TimeSlotViewSet, basename='timeslot')

urlpatterns = [
    path('', include(router.urls)),
] 