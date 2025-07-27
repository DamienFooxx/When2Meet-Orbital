from django.urls import path, include
from rest_framework.routers import DefaultRouter
from polls.views import PollViewSet, PollOptionViewSet, PollVoteViewSet

router = DefaultRouter()
router.register(r"polls", PollViewSet, basename="poll")
router.register(r"poll-options", PollOptionViewSet, basename="poll-option")
router.register(r"poll-votes", PollVoteViewSet, basename="poll-vote")

urlpatterns = [
    path("", include(router.urls)),
] 