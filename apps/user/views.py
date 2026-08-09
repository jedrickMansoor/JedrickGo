from rest_framework.response import Response
from rest_framework import status
from apps.user.models import User

from apps.user.serializers import UserSerializer
from apps.user.service import create_user

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from apps.user.pagination import UserPagination

from apps.user.filters import UserFilter


from rest_framework import viewsets
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth import authenticate


from rest_framework.permissions import  AllowAny,IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.account.serializer import AccountSerializer



class UserViewSet(ModelViewSet):
    
    authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]
    def get_permissions(self):
        if self.action in ["login", "create", "list", "retrieve"]:
            return [AllowAny()]
        if self.action in["partial_update", "update", "user_update"]:
            return [IsAuthenticated()]
        return [IsAdminUser()]
    
    queryset = User.objects.all().order_by("id")
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # FOR SEARCHING
    search_fields = ['email', 'phone_number', 'city']
    # FOR FILTERING
    filterset_class = UserFilter
    # FOR ORDERING
    ordering_fields = ['id','created_at']
    
    serializer_class = UserSerializer
    
    # PAGINATION
    pagination_class = UserPagination
    
    lookup_field = "id"
    lookup_url_kwarg = "id"
    
    # OVERRIDE QUERYSET
    def get_queryset(self):
        queryset = super().get_queryset()
        
        role = self.request.query_params.get("role")
        if role :
            queryset = User.objects.filter(role=role);
        
        return queryset
    
    
    
    # LOGIN USER
    @action(detail=False, methods=["post"])
    def login(self, request):

        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {   
                    "sucess" : False,
                    "message": "Email and password are required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(
            username=email,   
            password=password
        )

        if user is None:
            return Response(
                {"error": "Invalid email or password."},
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        

        refresh = RefreshToken.for_user(user)

        serializer = self.get_serializer(user)

        return Response({
            "success": True,
            "message": "User successfully logged in.",
            "user": {**serializer.data, "account": AccountSerializer(user.account).data},
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }, status=status.HTTP_201_CREATED)


    # USER UPDATE
    @action(detail=False, methods=["patch"], url_path="update-me")
    def user_update(self, request, *args, **kwargs):
        # Update User model
        user_data = {}

        if "password" in request.data:
            user_data["password"] = request.data["password"]

        if "phone_number" in request.data:
            user_data["phone_number"] = request.data["phone_number"]

        if user_data:
            user_serializer = self.get_serializer(
                request.user,
                data=user_data,
                partial=True
            )
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()

        # Update Account model
        account = request.user.account

        account_serializer = AccountSerializer(
            account,
            data=request.data,
            partial=True
        )
        account_serializer.is_valid(raise_exception=True)
        account_serializer.save()

        return Response(
            {
                "success": True,
                "message": "Account updated successfully",
                "user": {
                    **UserSerializer(request.user).data,
                    "account": AccountSerializer(request.user.account).data,
                },
            },
            status=status.HTTP_200_OK,
        )
    
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        users = self.get_serializer(queryset, many=True)
        return Response(
            {
                "success": True,
                "message": "Users was successfully fetched",
                "users": users.data
            },
            status=status.HTTP_200_OK,
        )


class CustomTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]
        
        
