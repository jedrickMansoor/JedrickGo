
from apps.product_category.models import ProductCategory
from apps.product_category.serializer import ProductCategorySerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import  AllowAny,IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from apps.product_category.permission import IsAdmin




class ProductCategoryViewSet(ModelViewSet):
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]
    
    queryset = ProductCategory.objects.all().order_by("id")    
    serializer_class = ProductCategorySerializer    
    lookup_field = "slug" 
    
    
    
    



    
    
