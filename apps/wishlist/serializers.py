from rest_framework import serializers

from apps.product.serializer import ProductListSerializer
from apps.wishlist.models import Wishlist


class WishlistSerializer(serializers.ModelSerializer):
    products = ProductListSerializer(many=True, read_only=True)

    class Meta:
        model = Wishlist
        fields = [
            'id',
            'account',
            'products',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'account', 'created_at', 'updated_at']


class WishlistCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = ['products']
