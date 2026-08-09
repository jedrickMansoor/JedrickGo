from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action


from apps.dashboard.service import DashboardService
from apps.deal.serailizers import DealSerializer, DealImageSerializer
from apps.product.models import Product
from apps.product.serializer import ProductCreateUpdateSerializer, ProductListSerializer
from django.shortcuts import get_object_or_404
from django.utils import timezone

from apps.notification.service import NotificationService
from apps.user.models import User

from rest_framework.views import APIView


class DashboardAPIView(APIView):

    def get(self, request):
        tpq = request.query_params.get('tpq', None) #top_products_quantity
        tsq = request.query_params.get('tsq', None) #top_sellers_quantity
        luq = request.query_params.get('luq', None) #latest_users_quantity
        roq = request.query_params.get('roq', None) #recent_orders_quantity
        pdr = request.query_params.get('pdr', 7) #product_date_range
        lsp = request.query_params.get('lsp', None) #low_stock_products_quantity

        if tpq is not None:
            try:
                tpq = int(tpq)
            except ValueError:
                return Response({"error": "Invalid value for top_products. Must be an integer."}, status=status.HTTP_400_BAD_REQUEST)
        
        if tsq is not None:
            try:
                tsq = int(tsq)
            except ValueError:
                return Response({"error": "Invalid value for top_sellers. Must be an integer."}, status=status.HTTP_400_BAD_REQUEST)

        if luq is not None:
            try:
                luq = int(luq)
            except ValueError:
                return Response({"error": "Invalid value for latest_users. Must be an integer."}, status=status.HTTP_400_BAD_REQUEST)

        if roq is not None:
            try:
                roq = int(roq)
            except ValueError:
                return Response({"error": "Invalid value for recent_orders. Must be an integer."}, status=status.HTTP_400_BAD_REQUEST)
        
        if pdr is not None:
            try:
                pdr = int(pdr)
            except ValueError:
                return Response({"error": "Invalid value for product_date_range. Must be an integer."}, status=status.HTTP_400_BAD_REQUEST)
        
        if lsp is not None:
            try:
                lsp = int(lsp)
            except ValueError:
                return Response({"error": "Invalid value for low_stock_products. Must be an integer."}, status=status.HTTP_400_BAD_REQUEST)
        
        
        if request.user.role == "seller":
            data = DashboardService.get_seller_summary(seller=request.user.account, tpq=tpq, lsp=lsp, luq=luq, roq=roq, days=pdr)
        else:
             data = DashboardService.get_summary(tpq=tpq, tsq=tsq, luq=luq, roq=roq)
        
        return Response(data)
    