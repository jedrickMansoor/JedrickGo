from rest_framework.routers import DefaultRouter

from apps.payment.views import PaymentViewSet

router = DefaultRouter()
router.register('payments', PaymentViewSet, basename='payments')

urlpatterns = router.urls
