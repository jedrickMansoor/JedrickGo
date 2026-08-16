from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.notification.views import NotificationViewSet
from .views import RegisterFCMTokenView, UnregisterFCMTokenView

router = DefaultRouter()
router.register('notifications', NotificationViewSet, basename='notifications')

urlpatterns = [
    path('fcm/register/', RegisterFCMTokenView.as_view(), name='fcm-register'),
    path('fcm/unregister/', UnregisterFCMTokenView.as_view(), name='fcm-unregister'),
]

# Append
urlpatterns += router.urls