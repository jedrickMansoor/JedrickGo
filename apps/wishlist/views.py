from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.product.models import Product
from apps.wishlist.models import Wishlist
from apps.wishlist.serializers import WishlistSerializer, WishlistCreateSerializer


class WishlistViewSet(ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Wishlist.objects.all().order_by('-created_at')
    serializer_class = WishlistSerializer

    def get_queryset(self):
        account = getattr(self.request.user, 'account', None)
        if account is None:
            return Wishlist.objects.none()
        return Wishlist.objects.filter(account=account).order_by('-created_at')

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return WishlistCreateSerializer
        return WishlistSerializer

    @action(detail=False, methods=['get', 'post', 'patch'])
    def me(self, request):
        wishlist, _ = Wishlist.objects.get_or_create(account=request.user.account)

        if request.method == 'GET':
            serializer = self.get_serializer(wishlist)
            return Response(serializer.data)

        serializer = self.get_serializer(
            wishlist,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='add-product')
    def add_product(self, request):
        wishlist, _ = Wishlist.objects.get_or_create(account=request.user.account)
        product_id = request.data.get('product_id')

        if not product_id:
            return Response({'success':False,'message': 'product is required.'}, status=400)

        product = Product.objects.filter(id=product_id).first()
        if product is None:
            return Response({'success':False,'message': 'Product not found.'}, status=404)

        wishlist.products.add(product)
        return Response({'success':True,'message':'Product was added', 'wishlist' : self.get_serializer(wishlist).data}, status=200)

    @action(detail=False, methods=['delete'],  url_path='remove-product')
    def remove_product(self, request):
        wishlist, _ = Wishlist.objects.get_or_create(account=request.user.account)
        product_id = request.data.get('product_id')

        if not product_id:
            return Response({'success':False,'message': 'product is required.'}, status=400)

        product = Product.objects.filter(id=product_id).first()
        if product is None:
            return Response({'success':False,'message': 'Product not found.'}, status=404)

        wishlist.products.remove(product)
        return Response({'success':True,'message':'Product was removed', 'wishlist' : self.get_serializer(wishlist).data}, status=200)
