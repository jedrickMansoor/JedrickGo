from rest_framework import serializers
from apps.account.models import Account


class AccountSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(required=False)

    class Meta:
        model = Account
        fields = [
            "id",
            "user",
            "first_name",
            "last_name",
            "phone_number",
            "profile_picture",
            "date_of_birth",
            "gender",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SellerAccountSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(required=False)
    total_products = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = [
            "id",
            "user",
            "first_name",
            "last_name",
            "phone_number",
            "profile_picture",
            "date_of_birth",
            "gender",
            "total_products",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
        
    def get_total_products(self, obj):
        if obj.user.role == "seller" :
            return obj.products.count()
        return None

class AccountMinimalSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(required=False)
    total_products = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = [
            "id",
            "first_name",
            "last_name",
            "profile_picture",
            "total_products",
        ]

    def get_total_products(self, obj):
        if obj.user.role == "seller" :
            return obj.products.count()
        return None
    
    
class TopSellerAccountSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(required=False)
    total_products = serializers.SerializerMethodField()
    total_sales = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = Account
        fields = [
            "id",
            "first_name",
            "last_name",
            "profile_picture",
            "total_products",
            "total_sales",
        ]

    def get_total_products(self, obj):
            if obj.user.role == "seller" :
                return obj.products.count()
            return None