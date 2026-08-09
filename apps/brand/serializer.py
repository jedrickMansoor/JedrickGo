from rest_framework import serializers
from .models import Brand
from apps.product_category.models import ProductCategory
from apps.product_category.serializer import ProductCategorySerializer


class CreateBrandSerializer(serializers.ModelSerializer):
    logo = serializers.ImageField(required=False)
    category = serializers.PrimaryKeyRelatedField(
        queryset=ProductCategory.objects.all()
    )
    

    class Meta:
        model = Brand
        fields = [
            "name",
            "slug",
            "logo",
            "category",
            
        ]
        read_only_fields = ["slug"]

class ListBrandSerializer(serializers.ModelSerializer):
    category = ProductCategorySerializer(read_only=True)
    logo = serializers.ImageField(required=False)

    class Meta:
        model = Brand
        fields = [
            "name",
            "slug",
            "logo",
            "category",
        ]
    
