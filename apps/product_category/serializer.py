from rest_framework import serializers
from apps.product_category.models import ProductCategory


class ProductCategorySerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)

    class Meta:
        model = ProductCategory
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "image",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["slug", "created_at", "updated_at"]

