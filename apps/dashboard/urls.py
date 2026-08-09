from django.urls import path
from .views import DashboardAPIView

urlpatterns = [
    path("dashboard/", DashboardAPIView.as_view(), name="dashboard"),
    # path("dashboard/revenue/", RevenueChartAPIView.as_view(), name="dashboard-revenue"),
]