from rest_framework.routers import DefaultRouter
from apps.account.views import AccountViewSet

router = DefaultRouter()

router.register("accounts", AccountViewSet, basename="accounts")

urlpatterns = router.urls
