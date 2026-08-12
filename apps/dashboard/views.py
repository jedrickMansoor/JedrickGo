from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

# MODELS
from apps.product.models import Product
from apps.account.models import Account
from apps.user.models import User
from apps.deal.models import Deal

# SERIALIZERS
from apps.deal.serailizers import DealSerializer, DealImageSerializer
from apps.product.serializer import ProductOrderItemSerializer
from apps.account.serializer import AccountMinimalSerializer


# SERVICES
from apps.dashboard.service import DashboardService
from apps.notification.service import NotificationService

# DJANGO
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q



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


class ContentAPIView(APIView):
    def get(self, request):
        search = request.query_params.get("search", None)

        # Helper to safely parse query parameters as booleans ("true", "1", etc.)
        def is_true(val):
            return str(val).lower() in ("true", "1", "yes")

        show_products = is_true(request.query_params.get("products", True))
        show_sellers = is_true(request.query_params.get("sellers", True))
        show_deals = is_true(request.query_params.get("deals", True))

        resp = {"sellers": [], "products": [], "deals": []}

        if not search:
            return Response(resp)

        if show_products:
            all_products = Product.objects.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
            resp["products"] = ProductOrderItemSerializer(
                all_products, many=True
            ).data

        if show_sellers:
            filtered_sellers = Account.objects.filter(
                user__role="seller"
            ).filter(
                Q(first_name__icontains=search) | Q(last_name__icontains=search)
            )
            resp["sellers"] = AccountMinimalSerializer(
                filtered_sellers, many=True
            ).data

        if show_deals:
            today = timezone.localdate()
            filtered_deals = Deal.objects.filter(
                Q(title__icontains=search) | Q(description__icontains=search),
                start_date__lte=today,  
                end_date__gte=today,  
                status="active",
            )
            resp["deals"] = DealSerializer(filtered_deals, many=True).data

        return Response(resp)