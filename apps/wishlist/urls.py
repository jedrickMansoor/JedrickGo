from rest_framework.routers import DefaultRouter

from apps.wishlist.views import WishlistViewSet

router = DefaultRouter()
router.register('wishlists', WishlistViewSet, basename='wishlists')

urlpatterns = router.urls
