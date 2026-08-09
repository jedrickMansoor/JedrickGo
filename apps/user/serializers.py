from rest_framework import serializers
from apps.user.models import User
from apps.account.serializer import AccountSerializer, SellerAccountSerializer


class UserSerializer(serializers.ModelSerializer):
    account = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "password",
            "phone_number",
            "role",
            "account"
        ]
        extra_kwargs = {
            "password": {
                "write_only": True
            }
        }
        
    def get_account(self, obj):
        if not hasattr(obj, "account"):
            return None
    
        if obj.role == "seller":
            return SellerAccountSerializer(obj.account).data
        elif obj.role == "customer":
            return AccountSerializer(obj.account).data
    
        return AccountSerializer(obj.account).data
    

    def create(self, validated_data):

        password = validated_data.pop("password")

        user = User(**validated_data)

        user.set_password(password)

        user.save()

        return user

    def update(self, instance, validated_data):

        password = validated_data.pop("password", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()

        return instance