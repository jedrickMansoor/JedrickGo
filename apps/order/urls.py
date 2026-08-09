from rest_framework.routers import DefaultRouter
from apps.order.views import OrderViewSet, OrderItemViewSet, SellerOrderAPIView
from django.urls import path, include

router = DefaultRouter()

router.register(r'orders', OrderViewSet, basename='order')
router.register(r'order-items', OrderItemViewSet, basename='orderitem')

urlpatterns = [
    path("orders/status/<int:id>/", SellerOrderAPIView.as_view(), name="seller_order"),
    path("", include(router.urls)),        
    ]