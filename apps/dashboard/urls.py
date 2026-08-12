from django.urls import path
from .views import DashboardAPIView
from .views import ContentAPIView
urlpatterns = [
    path("dashboard/", DashboardAPIView.as_view(), name="dashboard"),
    path("content/", ContentAPIView.as_view(), name="content"),
]