from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.cart.views import CartAPIView, CartItemViewSet

router = DefaultRouter()
router.register(r'cart-items', CartItemViewSet, basename='cart-item')

urlpatterns = [
    path("cart/", CartAPIView.as_view(), name="cart"),
    path("", include(router.urls)),
]