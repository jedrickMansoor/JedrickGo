from rest_framework.routers import DefaultRouter
from apps.product.views import ProductViewSet, ProductImageViewSet, ProductReviewViewSet

router = DefaultRouter()

router.register(r'products', ProductViewSet, basename='product')
router.register(r'reviews', ProductReviewViewSet, basename='review')
router.register(r'product-images', ProductImageViewSet, basename='product-image')

urlpatterns = router.urls