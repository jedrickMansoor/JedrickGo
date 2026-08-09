from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.user.views import UserViewSet
from apps.user.views import CustomTokenRefreshView

router = DefaultRouter()

router.register(
    "users",
    UserViewSet,
    basename="users"
)

urlpatterns = router.urls + [
    path(
        "token/refresh/",
        CustomTokenRefreshView.as_view(),
        name="token_refresh",
    ),
]