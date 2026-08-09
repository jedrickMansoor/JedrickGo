from rest_framework.routers import DefaultRouter
from apps.product_category.views import ProductCategoryViewSet

router = DefaultRouter()
router.register('product-categories', ProductCategoryViewSet, basename='product-category')

urlpatterns = router.urls