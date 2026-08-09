from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import  AllowAny,IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.product.permissions import IsSeller
from apps.product.serializer import ProductCreateUpdateSerializer, ProductImageSerializer, ProductListSerializer, ProductReviewSerializer
from apps.product.models import Product, ProductReview, ProductImage
from apps.product_category.models import ProductCategory
from rest_framework.response import Response
from rest_framework import status, viewsets 

from django.db import transaction
from django.core.files.storage import default_storage

from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta







class ProductViewSet(ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]
    queryset = Product.objects.all().order_by("id")    
    lookup_field = "slug"   
    
    # SERIALIZER OVERRIDE
    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ProductCreateUpdateSerializer
        return ProductListSerializer
    
    # PERMISSION OVERRIDE
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [AllowAny]
        elif self.action == "create":
            permission_classes = [IsAuthenticated, IsSeller]
        elif self.action in ["update", "partial_update", "destroy"]:
            permission_classes = [IsAuthenticated, IsSeller]
        else:
            permission_classes = [AllowAny]

        return [permission() for permission in permission_classes]
    
    # OVERRIDE QUERYSET
    def get_queryset(self):
        queryset = super().get_queryset()

        seller_id = self.request.query_params.get("seller")
        if seller_id:
            queryset = queryset.filter(seller_id=seller_id)

        category_slug = self.request.query_params.get("category")
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        p_type = self.request.query_params.get("ptype")
        if p_type == "new":
            queryset = queryset.filter(created_at__gte=timezone.now() - timedelta(days=1))

        return queryset
    
    # CREATE PRODUCT OVRIDE
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save(seller=request.user.account)

        images = request.FILES.getlist("images")

        for index, image in enumerate(images):
            ProductImage.objects.create(
                product=product,
                image=image,
                is_primary=(index == 0)
            )

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
        


    
# PRODUCT REVIEW VIEWSET
class ProductReviewViewSet(ModelViewSet):
    serializer_class = ProductReviewSerializer
    
    def get_queryset(self):
        queryset = ProductReview.objects.all().order_by("id")

        product_id = self.request.query_params.get("product")
        if product_id:
            queryset = queryset.filter(product_id=product_id)

        return queryset
    


class ProductImageViewSet(ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):

        product_id = request.data.get("product_id")

        if not product_id:
            return Response(
                {
                    "success": False,
                    "message": "product_id is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        product = get_object_or_404(Product, id=product_id)

        images = request.FILES.getlist("images")

        if not images:
            return Response(
                {
                    "success": False,
                    "message": "At least one image is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        has_primary = product.images.filter(is_primary=True).exists()

        for index, image in enumerate(images):
            ProductImage.objects.create(
                product=product,
                image=image,
                is_primary=(not has_primary and index == 0)
            )

        return Response(
            {
                "success": True,
                "message": "Product images uploaded successfully."
            },
            status=status.HTTP_201_CREATED
        )
    
