from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Collection
from .serializers import (
    CreateCollectionSerializer,
    ListCollectionSerializer,
)
from .permissions import IsAdminUserOnly


class CollectionViewSet(viewsets.ModelViewSet):
    queryset = Collection.objects.all().order_by("name")
    lookup_field = "slug"

    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAdminUserOnly()]

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return ListCollectionSerializer
        return CreateCollectionSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        creator_type = self.request.query_params.get("creator_type")
        seller = self.request.query_params.get("seller")

        if creator_type:
            queryset = queryset.filter(creator_type=creator_type)

        if seller:
            queryset = queryset.filter(seller_id=seller)

        return queryset