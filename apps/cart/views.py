from rest_framework.viewsets import ModelViewSet
from apps.cart.models import Cart, CartItem
from apps.cart.serializers import CartSerializer, CartItemSerializer, CartItemCreateUpdateSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import  AllowAny,IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import APIView, action
from rest_framework.mixins import CreateModelMixin, UpdateModelMixin, DestroyModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from apps.pricing.services import PricingService



# CART APIView
class CartAPIView(APIView):
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_cart(self):
        try:
            return Cart.objects.get(account=self.request.user.account)
        except Cart.DoesNotExist:
            return None
    
    def get(self, request, *args, **kwargs):
        cart = self.get_cart()
        if cart is None:
            return Response(
                {"success": True, "message": "Cart is empty", "data": {}},
                status=status.HTTP_200_OK,
            )
        serializer = CartSerializer(cart)
        cart_items = CartItem.objects.filter(cart=cart)
        cart_items_serializer = CartItemSerializer(cart_items, many=True)
        
        prices = PricingService.calculate_cart_prices(cart)
    
        return Response({
            "success": True,
            "message": 'cart items retrieved successfully',
            "data": {
                **serializer.data,
                "items": cart_items_serializer.data,
                "total_items": cart_items.count(),
                "total_price": prices["total_original_price"],
                "discounted_price": prices["total_discount_amount"],
                "final_price": prices["total_final_price"]
            }
        })


    
# CART ITEM VIEWSET
class CartItemViewSet(CreateModelMixin ,UpdateModelMixin, DestroyModelMixin, RetrieveModelMixin, GenericViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return CartItemCreateUpdateSerializer
        return CartItemSerializer
    
    def get_cart(self):
        try:
            return Cart.objects.get(account=self.request.user.account)
        except Cart.DoesNotExist:
            return None
    
    def get_queryset(self):
        cart = self.get_cart()
        if cart is None:
            return CartItem.objects.none()

        return CartItem.objects.filter(cart=cart)
    
    # ADD ITEM
    def create(self, request, *args, **kwargs):
        # Get the cart for the authenticated user
        cart, created = Cart.objects.get_or_create(account=request.user.account)
        
        # Create a new cart item and associate it with the user's cart
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        product = serializer.validated_data["product"]
        quantity = serializer.validated_data["quantity"]
        
        # Check the stock
        if quantity > product.stock_quantity :
            return Response(
                {"error": 
                    f"Insufficient stock, please reduce the quantity for {product.name} atmost {product.stock_quantity}."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # Check if the product is already in the cart
        cart_item = CartItem.objects.filter(cart=cart, product=product).first()
        
        if cart_item is None:
            cart_item_prices = PricingService.calculate_cart_item(product=product, quantity=quantity)
            
            cart_item = serializer.save(
                cart=cart,
                original_price=cart_item_prices["original_price"],
                discount_amount=cart_item_prices["discount_amount"],
                final_price=cart_item_prices["final_price"],
            )
        else:
            new_quantity = cart_item.quantity + quantity

            if new_quantity > product.stock_quantity:
                return Response(
                    {"error": f"Only {product.stock_quantity} items are available."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
                
            cart_item.quantity = new_quantity

            cart_item_prices = PricingService.calculate_cart_item(
                product=product,
                quantity=new_quantity
            )

            cart_item.original_price = cart_item_prices["original_price"]
            cart_item.discount_amount = cart_item_prices["discount_amount"]
            cart_item.final_price = cart_item_prices["final_price"]

            cart_item.save()

        return Response({
            "success" : True,
            "message" : 'Item was added to the cart',
            "item" : self.get_serializer(cart_item).data,
            },
            status=status.HTTP_201_CREATED,
        )
    
    # UPDATE
    def update(self, request, *args, **kwargs):
        cart_item = self.get_object()
        serializer = self.get_serializer(cart_item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        product = cart_item.product
        new_quantity = serializer.validated_data.get("quantity", cart_item.quantity)

        # Check the stock
        if new_quantity > product.stock_quantity:
            return Response(
                {"error": f"Insufficient stock, please reduce the quantity for {product.name} atmost {product.stock_quantity}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart_item_prices = PricingService.calculate_cart_item(product=product, quantity=new_quantity)
        
        serializer.save(
            original_price=cart_item_prices["original_price"],
            discount_amount=cart_item_prices["discount_amount"],
            final_price=cart_item_prices["final_price"]
        )
        return Response(serializer.data)