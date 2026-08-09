
from apps.account.models import Account
from apps.account.serializer import AccountSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import  AllowAny,IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response




class AccountViewSet(ModelViewSet):
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    queryset = Account.objects.all().order_by("id")    
    serializer_class = AccountSerializer
    
    @action(detail=False, methods=["get", "patch"])
    def me(self, request):
        account = request.user.account

        if request.method == "GET":
            serializer = self.get_serializer(account)
            return Response(serializer.data)

        serializer = self.get_serializer(
            account,
            data=request.data,
            partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)



    
    
