from rest_framework import serializers
from apps.cart.models import Cart, CartItem
from apps.product.serializer import ProductListSerializer

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = [
            "id",
            "account",
        ]

        
class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "product", "quantity", "original_price", "discount_amount", "final_price"]
        read_only_fields = ["original_price", "discount_amount", "final_price"]


class CartItemCreateUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CartItem
        fields = ["product", "quantity"]