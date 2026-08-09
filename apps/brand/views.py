from rest_framework import viewsets
from .models import Brand
from apps.brand.serializer import CreateBrandSerializer, ListBrandSerializer
from rest_framework.permissions import  AllowAny,IsAuthenticated, IsAdminUser
from apps.brand.permissions import IsAdminUserOnly
from rest_framework_simplejwt.authentication import JWTAuthentication



class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all().order_by("name")
    lookup_field = "slug"
    authentication_classes = [JWTAuthentication]
        # permission_classes = [IsAuthenticated]
        
    def get_queryset(self):
        queryset = super().get_queryset()

        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(category__slug=category)

        return queryset
    
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAdminUserOnly()]
    
    def get_serializer_class(self, *args, **kwargs):
        if self.action in ["list", "retrieve"]:
            return ListBrandSerializer
        return CreateBrandSerializer
        