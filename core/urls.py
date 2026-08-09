from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.user.urls')),
    path('api/', include('apps.account.urls')),
    path ('api/', include('apps.product.urls')),
    path('api/', include('apps.product_category.urls')),
    path('api/', include('apps.cart.urls')),  
    path('api/', include('apps.order.urls')), 
    path('api/', include('apps.deal.urls')), 
    path('api/', include('apps.notification.urls')), 
    path('api/', include('apps.wishlist.urls')), 
    path('api/', include('apps.payment.urls')), 
    path('api/', include('apps.brand.urls')), 
    path('api/', include('apps.collection.urls')), 
    # path('api/', include('apps.chat.urls')),
    path('api/', include('apps.dashboard.urls')),
]
