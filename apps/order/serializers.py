from rest_framework import serializers
from apps.order.models import Order, OrderItem, SellerOrder
from apps.product.serializer import ProductListSerializer


class OrderCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'id',
            'shipping_address',
            'phone_number',
            'payment_method',
        ]
        
class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = '__all__'

class SellerOrderListSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = SellerOrder
        fields = [
            "id",
            "order",
            "seller",
            "items",
            "subtotal",
            "discounted",
            "total",
            "status",
            "created_at",
            "updated_at",
        ]

class OrderListSerializer(serializers.ModelSerializer):
    seller_orders = SellerOrderListSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Order
        fields = "__all__"
        
        

class SellerOrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = SellerOrder
        fields = [
            "id",
            "order",
            "seller",
            "items",
            "subtotal",
            "discounted",
            "total",
            "status",
            "created_at",
            "updated_at",
        ]

class SellerOrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerOrder
        fields = ["status"]