from rest_framework import serializers

from apps.deal.models import Deal, DealImage

# DEAL IMAGE
class DealImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    class Meta:
        model = DealImage
        fields = [
            "id",
            "image",
        ]
    
    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None

# DEAL 
class DealSerializer(serializers.ModelSerializer):
    image = DealImageSerializer(read_only=True)
    
    class Meta:
        model = Deal
        fields = [
            "id",
            "slug",
            "products",
            "seller",
            "title",
            "description",
            "type",
            "color",
            "creator_type",
            "value",
            "start_date",
            "end_date",
            "status",
            "priority",
            "image",
            "created_at",
            "updated_at",
        ]

    def validate_priority(self, value):
        request = self.context["request"]

        if request.user.role == "admin" and value < 5:
            value += 5

        if request.user.role == "seller" and value > 5:
            value -= 5

        return value
