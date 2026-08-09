from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action


from apps.deal.models import Deal, DealImage
from apps.deal.serailizers import DealSerializer, DealImageSerializer
from apps.product.models import Product
from apps.product.serializer import ProductCreateUpdateSerializer, ProductListSerializer
from django.shortcuts import get_object_or_404
from django.utils import timezone

from apps.notification.service import NotificationService
from apps.user.models import User

class DealViewSet(ModelViewSet):
    authentication_classes = [JWTAuthentication]
    queryset = Deal.objects.all().order_by("-created_at")
    serializer_class = DealSerializer
    lookup_field = "slug"

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        today = timezone.now().date()

        seller_id = self.request.query_params.get("seller")
        if seller_id:
            queryset = queryset.filter(seller_id=seller_id)

        deal_type = self.request.query_params.get("dtype")
        
        if deal_type == "admin":
                    queryset = queryset.filter(
                        creator_type="admin",
                        status="active",
                        start_date__lte=today,
                        end_date__gte=today,
                    ).order_by("-priority")

        if deal_type == "pwmc":
            queryset = queryset.filter(
                creator_type="admin",
                status="active",
                start_date__lte=today,
                end_date__gte=today,
                priority__gte=8,
                priority__lte=10,
            ).order_by("-priority")

        elif deal_type == "psc":
            queryset = queryset.filter(
                creator_type="admin",
                status="active",
                start_date__lte=today,
                end_date__gte=today,
                priority__gte=6,
                priority__lte=7,
            ).order_by("-priority")

        return queryset
    

     # SINGLE DEAL
    def retrieve(self, request, *args, **kwargs):
        deal = self.get_object()
        deal_serializer = self.get_serializer(deal)
        
        products = deal.products.all()
        
        products_serializer = ProductListSerializer(products, many=True)

        return Response(
            {
                "success": True,
                "message": "Deal fetched successfully.",
                "deal": deal_serializer.data,
                "products" : products_serializer.data
            },
            status=status.HTTP_200_OK,
        )
        
    
    # BEST DEALS 
    def list(self, request, *args, **kwargs):
        deals = self.get_queryset()

        serializer = self.get_serializer(deals, many=True)

        return Response(
            {
                "success": True,
                "message": "Successfully fetched deals",
                "deals": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
    
   
    
    
    # CREATE DEAL
    def create(self, request, *args, **kwargs):

        if request.user.role not in ["seller", "admin"]:
            return Response(
                {
                    "success": False,
                    "message": "Only sellers and admins can create deals.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        seller_account = None
        creator_type = ""

        if request.user.role == "seller":
            seller_account = request.user.account
            creator_type = "seller"

        else:
            creator_type = "admin"

        deal = serializer.save(
            seller=seller_account,
            creator_type=creator_type,
        )

        image = request.FILES.get("image")

        if image:
            deal_image, _ = DealImage.objects.get_or_create(
                deal=deal
            )

            deal_image.image = image
            deal_image.save()

        # Send Notifications
        if request.user.role == "seller":

            NotificationService.send_to_customers(
                sender=seller_account,
                notification_type="new_deal",
                title="New Deal",
                message=f"{deal.title} is now available.",
                target=deal,
            )

        else:

            NotificationService.send_to_non_admins(
                notification_type="new_deal",
                title="New Deal",
                message=f"{deal.title} is now available.",
                target=deal,
            )

        return Response(
            {
                "success": True,
                "message": "Successfully deal created.",
                "deal": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )
            
    # ADD PRODUCT
    @action(detail=True, methods=["patch"], url_path="add-product")
    def add_product(self, request, slug=None):
        deal = self.get_object()

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

        if deal.products.filter(id=product.id).exists():
            return Response(
                {
                    "success": False,
                    "message": "Product is already added to this deal."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Fixed discount cannot exceed product price
        if deal.type == "fixed" and deal.value >= product.price:
            return Response(
                {
                    "success": False,
                    "message": "Fixed discount cannot be greater than or equal to the product price."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        deal.products.add(product)

        return Response(
            {
                "success": True,
                "message": "Product added successfully."
            },
            status=status.HTTP_200_OK
        )
        
    
    # REMOVE PRODUCT
    @action(detail=True, methods=["patch"], url_path="remove-product")
    def remove_product(self, request, slug=None):
        deal = self.get_object()

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

        if not deal.products.filter(id=product.id).exists():
            return Response(
                {
                    "success": False,
                    "message": "Product is not associated with this deal."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        deal.products.remove(product)

        return Response(
            {
                "success": True,
                "message": "Product removed successfully."
            },
            status=status.HTTP_200_OK
        )
    
    
    # GET DEAL PRODUCTS
    @action(detail=True, methods=["get"], url_path="products")
    def get_products(self, request, slug=None):
        deal = Deal.objects.get(slug=slug)

        deal_serializer = DealSerializer(deal)
        product_serializer = ProductListSerializer(
            deal.products.all(),
            many=True
        )

        return Response(
            {
                "success": True,
                "deal": deal_serializer.data,
                "products": product_serializer.data,
            },
            status=status.HTTP_200_OK
        )
    
    # GET DEAL PRODUCTS
    @action(detail=False, methods=["get"], url_path="best")
    def get_best_deal(self, request):
        
        today = timezone.now().date()
        
        best_products = Product.objects.filter(
            deals__status="active",
            deals__start_date__lte=today,
            deals__end_date__gte=today,
        ).order_by("-deals__priority").distinct()

        
        product_serializer = ProductListSerializer(
            best_products,
            many=True
        )

        return Response(
            {
                "success": True,
                "products": product_serializer.data,
            },
            status=status.HTTP_200_OK
        )
        
        
    
    # GET DEAL PRODUCTS
    @action(detail=False, methods=["get"], url_path="my")
    def get_my_deal(self, request):
        
        today = timezone.now().date()
        
        deals = Deal.objects.filter(
            status="active",
            seller=request.user.account,
        ).order_by("-priority")
        
        serializer = self.get_serializer(deals, many=True)
        
        admin_deals = Deal.objects.filter(
            creator_type='admin',
            status="active",
            start_date__lte = today,
            end_date__gte = today,
        ).order_by("-priority")
        
        admin_serializer = self.get_serializer(admin_deals, many=True)
        
        return Response(
            {
                "success": True,
                "myDeals": serializer.data,
                "adminDeals" :admin_serializer.data,
            },
            status=status.HTTP_200_OK
        )
        
    
class DealImageViewSet(ModelViewSet):
    queryset = DealImage.objects.all()
    serializer_class = DealImageSerializer
    permission_classes = [IsAuthenticated]

    # ADD/UPDATE DEAL IMAGE
    def create(self, request, *args, **kwargs):
        deal_id = request.data.get("deal_id")

        if not deal_id:
            return Response(
                {
                    "success": False,
                    "message": "deal_id is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        deal = get_object_or_404(Deal, id=deal_id)

        image = request.FILES.get("image")

        if not image:
            return Response(
                {
                    "success": False,
                    "message": "Image was not provided."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        deal_image, created = DealImage.objects.get_or_create(
            deal=deal
        )

        deal_image.image = image
        deal_image.save()

        return Response(
            {
                "success": True,
                "message": "Deal image uploaded successfully."
            },
            status=status.HTTP_201_CREATED
        )