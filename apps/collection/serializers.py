from rest_framework import serializers
from .models import Collection
from apps.account.serializer import AccountSerializer


class CreateCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = [
            "id",
            "name",
            "slug",
            "creator_type",
            "seller",
        ]
        read_only_fields = [
            "id",
            "slug",
        ]


class ListCollectionSerializer(serializers.ModelSerializer):
    seller = AccountSerializer(read_only=True)

    class Meta:
        model = Collection
        fields = [
            "id",
            "name",
            "slug",
            "creator_type",
            "seller",
        ]