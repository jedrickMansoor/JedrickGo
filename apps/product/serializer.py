from django.utils import timezone
from rest_framework import serializers

from apps.deal.serailizers import DealSerializer
from apps.product.models import Product, ProductReview, ProductImage

from apps.account.serializer import AccountMinimalSerializer
from django.db.models import Avg

class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "price",
            "category",
            "slug",
            "stock_quantity",
        ]
        read_only_fields = ["slug"]
        
        
class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    class Meta:
        model = ProductImage
        fields = [
            "id",
            "image",
            "is_primary",
        ]
    
    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None



class ProductListSerializer(serializers.ModelSerializer):
    seller = AccountMinimalSerializer(read_only=True)
    category = serializers.StringRelatedField()
    active_deal = serializers.SerializerMethodField()
    discounted_price = serializers.SerializerMethodField()
    
    images = ProductImageSerializer(many=True, read_only=True)
    
    # Calculated average rating
    avg_rating = serializers.SerializerMethodField()
    total_reviews = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "seller",
            "category",
            "name",
            "slug",
            "stock_quantity",
            "description",
            "price",
            "images",
            "active_deal",
            "avg_rating",
            "total_reviews",
            "discounted_price",
            "created_at",
            "updated_at",
        ]
        
    def get_active_deal(self, obj):
        today = timezone.now().date()

        deal = obj.deals.filter(
            status="active",
            start_date__lte=today,
            end_date__gte=today,
        ).order_by("-priority").first()

        if deal:
            return DealSerializer(deal).data

        return None
    
    def get_discounted_price(self, obj):
        today = timezone.now().date()

        deal = obj.deals.filter(
            status="active",
            start_date__lte=today,
            end_date__gte=today,
        ).order_by("-priority").first()

        if not deal:
            return obj.price

        if deal.type == "percentage":
            return obj.price - (obj.price * deal.value / 100)

        elif deal.type == "fixed":
            return max(obj.price - deal.value, 0)

        return obj.price

    def get_avg_rating(self, obj):
        if hasattr(obj, 'annotated_avg_rating') and obj.annotated_avg_rating is not None:
            return round(obj.annotated_avg_rating, 1)
        
        avg = obj.reviews.aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg is not None else 0.0

    def get_total_reviews(self, obj):
        if hasattr(obj, 'annotated_total_reviews') and obj.annotated_total_reviews is not None:
            return obj.annotated_total_reviews
        
        return obj.reviews.count()

# PRODUCT ORDER ITEM
class ProductOrderItemSerializer(serializers.ModelSerializer):
    seller = AccountMinimalSerializer(read_only=True)
    category = serializers.StringRelatedField()
    
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "seller",
            "category",
            "name",
            "slug",
            "description",
            "images",
        ]

# PRODUCT REVIEW
class ProductReviewSerializer(serializers.ModelSerializer):
    product = serializers.SlugRelatedField(
        slug_field="slug",
        queryset=Product.objects.all()
    )
    
    account = AccountMinimalSerializer(read_only=True)

    class Meta:
        model = ProductReview
        fields = [
            "id",
            "account",
            "product",
            "rating",
            "comment",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class TopProductSerializer(serializers.ModelSerializer):
    sold = serializers.IntegerField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "price",
            "sold"
        ]