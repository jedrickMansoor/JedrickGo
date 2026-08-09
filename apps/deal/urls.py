from rest_framework.routers import DefaultRouter

from apps.deal.views import DealViewSet, DealImageViewSet

router = DefaultRouter()
router.register(r"deals", DealViewSet, basename="deal")
router.register(r"deal-images", DealImageViewSet, basename="deal-image")

urlpatterns = router.urls
