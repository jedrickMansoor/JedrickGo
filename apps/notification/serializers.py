from rest_framework import serializers

from apps.notification.models import Notification


from apps.order.models import Order, SellerOrder
from apps.product.models import Product
from apps.deal.models import Deal

from apps.product.serializer import ProductListSerializer
from apps.deal.serailizers import DealSerializer
from apps.account.serializer import AccountMinimalSerializer
from apps.order.serializers import OrderListSerializer, SellerOrderSerializer

class NotificationSerializer(serializers.ModelSerializer):
    target = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = "__all__"

    def get_target(self, obj):
        target = obj.target

        if target is None:
            return None

        if isinstance(target, Product):
            return ProductListSerializer(target).data

        if isinstance(target, Deal):
            return DealSerializer(target).data

        if isinstance(target, Order):
            return OrderListSerializer(target).data

        if isinstance(target, SellerOrder):
            return SellerOrderSerializer(target).data

        return None
