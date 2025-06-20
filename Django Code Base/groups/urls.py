from rest_framework.routers import DefaultRouter
from groups.views import GroupViewSet

router = DefaultRouter()
router.register(r'groups', GroupViewSet, basename = 'group')

urlpatterns = router.urls