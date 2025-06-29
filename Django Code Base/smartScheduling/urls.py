from django.urls import path, include
from rest_framework.routers import DefaultRouter
from smartScheduling.views import SchedulingViewSet

router = DefaultRouter()
router.register(r'smartschedule', SchedulingViewSet, basename = 'smartschedule')

urlpatterns = [
    path('', include(router.urls)),
]