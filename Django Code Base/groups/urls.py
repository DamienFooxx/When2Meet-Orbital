from rest_framework.routers import DefaultRouter
from groups.views import GroupViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'groups', GroupViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]

