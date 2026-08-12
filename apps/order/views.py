from rest_framework.viewsets import ModelViewSet
from apps.cart.models import Cart
from apps.notification.service import NotificationService
from apps.order.models import Order, OrderItem, SellerOrder
from apps.order.serializers import OrderCreateUpdateSerializer, OrderListSerializer, OrderItemSerializer, SellerOrderSerializer, SellerOrderUpdateSerializer

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import  AllowAny,IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from rest_framework.decorators import APIView, action

from apps.order.permissions import IsAdminUserOnly
from collections import defaultdict

from apps.product.models import Product
from django.db.models import F
from apps.order.utils import update_order_status

from apps.pricing.services import PricingService





# ORDER VIEWSET
class OrderViewSet(ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    
    
    # GET PERMISSION
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        elif self.action == 'create':
            return [IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAdminUserOnly()]
        return super().get_permissions()
    
    
    # GET CART
    def get_cart(self):
        try:
            return Cart.objects.get(account=self.request.user.account)
        except Cart.DoesNotExist:
            return None
    
    # SERIALIZERS
    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return OrderCreateUpdateSerializer

        if self.action in ["list", "retrieve"] and self.request.user.role == "seller":
            return SellerOrderSerializer

        return OrderListSerializer
    
    # QUERYSET
    def get_queryset(self):
        if self.request.user.role == "admin":
            return Order.objects.all().order_by('-created_at')
        if self.request.user.role == "seller":
            return SellerOrder.objects.filter(
            seller=self.request.user.account
        ).order_by('-created_at')
        return Order.objects.filter(account=self.request.user.account).order_by('-created_at')
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status != "pending":
            return Response(
                {
                    "success": False,
                    "message": "Only pending orders can be deleted.",
                    "data": {},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        instance.delete()
        return Response(   
            {   
                "success": True,
                "message": "Order deleted successfully.",
            })    
    
    
    # CREATE ORDER
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        
        cart = self.get_cart()
        if cart is None:
            return Response(
                {
                    "success": False,
                    "message": "Cart is empty. Cannot create order.",
                    "data": {},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        cart_items = cart.items.all()
        
        if not cart_items.exists():
            return Response(
                {
                    "success": False,
                    "message": "Cart is empty. Cannot create order.",
                    "data": {},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
            
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        for item in cart_items:
            if item.quantity > item.product.stock_quantity:
                return Response(
                    {
                        "success": False,
                        "message": f"Not enough stock for product {item.product.name}. Available: {item.product.stock_quantity}, Requested: {item.quantity}",
                        "data": {},
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        
        prices = PricingService.calculate_cart_prices(cart)
        
        order = serializer.save(account=request.user.account, total_amount=prices["total_final_price"])
        
        headers = self.get_success_headers(serializer.data)
        
        # Group items by seller
        seller_items = defaultdict(list)

        for item in cart_items:
            seller_items[item.product.seller].append(item)

        for seller, items in seller_items.items():
            subtotal = sum(
                item.original_price for item in items
            )
            
            discounted = sum(
                item.discount_amount
                for item in items
            )

            total = subtotal - discounted

            seller_order = SellerOrder.objects.create(
                order=order,
                seller=seller,
                subtotal=subtotal,
                discounted=discounted,
                total=total
            )
            
            # SEND NOTIFICATION TO SELLER
            NotificationService.send(
                notification_type="order_created",
                recipient=seller,
                title="New Order Created",
                message=f"An order has been created.",
                target=seller_order,
            )

            # Create order items for this seller
            for item in items:
                OrderItem.objects.create(
                    seller_order=seller_order,
                    product=item.product,
                    quantity=item.quantity,
                    original_price=item.original_price,
                    discount_amount=item.discount_amount,
                    final_price=item.final_price
                )

                product = item.product
                product.stock_quantity -= item.quantity
                product.save()
                
        cart.items.all().delete()
        
        return Response(
            {
                "success": True,
                "message": "Order created successfully",
                "data": {**serializer.data, "items": OrderItemSerializer(cart.items.select_related("product", "product__seller"), many=True).data},
            },
            status=status.HTTP_201_CREATED,
            headers=headers,
        )
    
    # RETRIEVE ORDER 
    def retrieve(self, request, *args, **kwargs):
        order = self.get_object()

        serializer = self.get_serializer(order)

        return Response({
            "success": True,
            "message": "Order retrieved successfully",
            "data": serializer.data,
        })
    
    
    # PATCH
    def partial_update(self, request, *args, **kwargs):
        order = self.get_object()

        # Example business rule
        if order.status == "delivered":
            return Response(
                {
                    "success": False,
                    "message": "Delivered orders cannot be updated.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(
            order,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "success": True,
                "message": "Order updated successfully.",
                "order": OrderListSerializer(order).data,
            },
            status=status.HTTP_200_OK,
        )
    
    
# ORDER ITEM VIEWSET
class OrderItemViewSet(ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    queryset = OrderItem.objects.all().order_by('-created_at')
    serializer_class = OrderItemSerializer
    
# SELLER ORDER
class SellerOrderAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    # UPDATE SELLER ORDER
    @transaction.atomic
    def patch(self, request, id):
        try:
            seller_order = SellerOrder.objects.get(id=id)
        except SellerOrder.DoesNotExist:
           return Response(
                {
                    "success": False,
                    "message": "No seller order found",
                },
                status=status.HTTP_404_NOT_FOUND,
           )
        
        if seller_order.seller != request.user.account:
            return Response(
                {
                    "success": False,
                    "message": "You do not have permission to update this order.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )
    
        data = request.data
            
        if seller_order.status == 'cancelled':
            return Response(
                {
                    "success": False,
                    "message": "Cannot change the status for already cancelled order",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
            
        serializer = SellerOrderUpdateSerializer(
            seller_order,
            data=request.data,
            partial=True
        )
        
        serializer.is_valid(raise_exception=True)
        
        updated_order = serializer.save()
        
        notification = NotificationService.get_order_notification(updated_order.status)
        
        # SEND NOTIFICATION TO SELLER
        NotificationService.send(
            notification_type=notification["notification_type"],
            recipient=updated_order.order.account,
            title=notification["title"],
            message=notification["message"],
            target=seller_order,
        )
        
        
        order_items = OrderItem.objects.filter(seller_order=seller_order)
        
        if serializer.validated_data.get("status") == "cancelled":
            for item in order_items:
                Product.objects.filter(id=item.product_id).update(
                stock_quantity=F("stock_quantity") + item.quantity
                )
        
        update_order_status(seller_order.order)
        
        
        
        return Response(
            {
                "success": True,
                "message": "Seller order updated successfully.",
                "data": serializer.data,
            }
        )
        