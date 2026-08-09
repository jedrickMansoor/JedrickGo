
from datetime import timedelta
from time import timezone

from django.utils import timezone
from django.db.models.aggregates import Sum
from django.db.models.functions import TruncDate

from apps import order
from apps.account.models import Account
from apps.account.serializer import AccountMinimalSerializer, TopSellerAccountSerializer
from apps.deal.models import Deal
from apps.notification.consumers import User
from apps.order.models import Order, OrderItem, SellerOrder
from apps.order.serializers import SellerOrderSerializer, OrderListSerializer
from apps.product.models import Product
from apps.product.serializer import ProductListSerializer, TopProductSerializer

from django.db.models import Count, Q



class DashboardService:

    @staticmethod
    def get_summary(tpq=None, tsq=None, luq=None, roq=None, pdr=7):
        revenue = Order.objects.aggregate(total_revenue=Sum('total_amount'))['total_revenue'] or 0
        # RETURNING THE SUMMARY DATA AS A DICTIONARY
        return {
            "total_customers": User.objects.filter(role="customer").count(),
            "total_sellers": User.objects.filter(role="seller").count(),
            "total_orders": Order.objects.count(),
            "total_products": Product.objects.count(),
            "total_revenue": revenue,
            "deals": DashboardService.get_deals_summary(),
            "orders": DashboardService.get_order_summary(),
            "seller_orders": DashboardService.get_seller_order_summary(),
            "revenue" : DashboardService.seller_revenue_chart(days=pdr),
            "recent_orders": {
                "count" : len(DashboardService.get_recent_orders(limit=roq)),
                "orders" : DashboardService.get_recent_orders(limit=roq)
            },
            "top_products": DashboardService.get_top_products(limit=tpq),
            "top_sellers": DashboardService.get_top_sellers(limit=tsq),
            "latest_users": DashboardService.latest_users(limit=luq),
        }

    
    @staticmethod
    def get_deals_summary():
        # DEALS
        return Deal.objects.aggregate(
            total=Count("id"),
            active=Count("id", filter=Q(status="active")),
            disabled=Count("id", filter=Q(status="disabled")),
            expired=Count("id", filter=Q(status="expired")),
            draft=Count("id", filter=Q(status="draft")),
            admin=Count("id", filter=Q(creator_type="admin")),
            seller=Count("id", filter=Q(creator_type="seller")),
        )
          

    @staticmethod
    def get_order_summary():
        # ORDERS
        return Order.objects.aggregate(
            total=Count("id"),
            pending=Count("id", filter=Q(status="pending")),
            confirmed=Count("id", filter=Q(status="confirmed")),
            processing=Count("id", filter=Q(status="processing")),
            shipped=Count("id", filter=Q(status="shipped")),
            delivered=Count("id", filter=Q(status="delivered")),
            cancelled=Count("id", filter=Q(status="cancelled")),
        )        
    
    @staticmethod
    def get_seller_order_summary():
        # ORDERS
        return SellerOrder.objects.aggregate(
            total=Count("id"),
            pending=Count("id", filter=Q(status="pending")),
            confirmed=Count("id", filter=Q(status="confirmed")),
            processing=Count("id", filter=Q(status="processing")),
            shipped=Count("id", filter=Q(status="shipped")),
            delivered=Count("id", filter=Q(status="delivered")),
            cancelled=Count("id", filter=Q(status="cancelled")),
        ) 
    
    @staticmethod
    def get_recent_orders(limit=None):
        orders = Order.objects.order_by("-created_at")
        orders = orders[:limit] if limit is not None else orders
        order_serializer = OrderListSerializer(orders, many=True)
        return order_serializer.data


    @staticmethod
    def get_top_products(limit=None, seller=None):
        # TOP PRODUCTS
        if seller is not None:
            top_products = (
                Product.objects
                .filter(seller=seller)
                .annotate(
                    sold=Sum(
                        "order_items__quantity",
                        filter=Q(order_items__seller_order__status="delivered")
                    )
                )
                .filter(sold__isnull=False)
                .order_by("-sold")
            )
        else:
            top_products = (
                Product.objects
                .annotate(
                    sold=Sum(
                        "order_items__quantity",
                        filter=Q(order_items__seller_order__status="delivered")
                    )
                )
                .filter(sold__isnull=False)
                .order_by("-sold")
            )
        
        top_products = top_products[:limit] if limit is not None else top_products

        serializer = TopProductSerializer(top_products, many=True)
        return serializer.data
        
            
    @staticmethod
    def get_top_sellers(limit=None):
        accounts = (
            Account.objects
            .filter(user__role="seller")
            .annotate(
                total_sales=Sum(
                    "seller_orders__total",
                    filter=Q(seller_orders__status="delivered")
                )
            )
            .filter(total_sales__isnull=False)
            .order_by("-total_sales")
        )
        
        accounts = accounts[:limit] if limit is not None else accounts
        
        serializer = TopSellerAccountSerializer(accounts, many=True)
        return serializer.data  


    @staticmethod
    def latest_users(limit=None):
        # LATEST USERS
        queryset = Account.objects.order_by("-created_at")
        queryset = queryset[:limit] if limit is not None else queryset
        serializer = AccountMinimalSerializer(queryset, many=True)
        return serializer.data
    
    
    @staticmethod
    def get_seller_summary(seller=None, tpq=None, lsp=None, luq=None, roq=None, days=7):
        if seller is None:
            return []
                
        return {
            "products" : Product.objects.filter(seller=seller).count(),
            "orders" : SellerOrder.objects.filter(seller=seller).count(),
            "pending_orders" : SellerOrder.objects.filter(seller=seller, status="pending").count(),
            "revenue" : DashboardService.seller_revenue_chart(seller=seller, days=days),
            "order_status" : DashboardService.get_seller_orders_status(seller=seller),
            "recent_orders" : {
                "count" : len(DashboardService.get_seller_recent_orders(limit=roq, seller=seller)),
                "orders" : DashboardService.get_seller_recent_orders(limit=roq, seller=seller)
            },
            "top_products" : DashboardService.get_top_products(limit=tpq, seller=seller),
            "low_stock_products" : DashboardService.get_seller_low_stock_products(limit=lsp, seller=seller)
        }
    
    
    @staticmethod
    def seller_revenue_chart(days=7, seller=None):
        today = timezone.localdate()
        start_date = today - timedelta(days=days - 1)

        queryset = SellerOrder.objects.filter(
            status="delivered",
            created_at__date__gte=start_date
        )

        if seller is not None:
            queryset = queryset.filter(seller=seller)

        revenue = (
            queryset
            .annotate(date=TruncDate("updated_at"))
            .values("date")
            .annotate(total_revenue=Sum("total"))
        )

        revenue_map = {
            item["date"]: item["total_revenue"]
            for item in revenue
        }

        chart = []

        for i in range(days):
            date = start_date + timedelta(days=i)

            chart.append({
                "date": date,
                "total_revenue": revenue_map.get(date, 0)
            })

        return chart
    
    
    @staticmethod
    def get_seller_recent_orders(limit=None, seller=None):
        if seller is None:
            return []
        orders = SellerOrder.objects.filter(seller=seller).order_by("-created_at")[:limit] if limit is not None else SellerOrder.objects.filter(seller=seller).order_by("-created_at")
        
        serializer = SellerOrderSerializer(orders, many=True)
        return serializer.data

    @staticmethod
    def get_seller_orders_status(limit=None, seller=None):
        if seller is None:
            return []
        
        return SellerOrder.objects.filter(seller=seller).aggregate(
            total=Count("id"),
            pending=Count("id", filter=Q(status="pending")),
            confirmed=Count("id", filter=Q(status="confirmed")),
            processing=Count("id", filter=Q(status="processing")),
            shipped=Count("id", filter=Q(status="shipped")),
            delivered=Count("id", filter=Q(status="delivered")),
            cancelled=Count("id", filter=Q(status="cancelled")),
        )
    
    
    @staticmethod
    def get_seller_low_stock_products(limit=None, seller=None):
        if seller is None:
            return []
        
        low_stock_products = Product.objects.filter(seller=seller, stock_quantity__lte=5).order_by("stock_quantity")
        low_stock_products = low_stock_products[:limit] if limit is not None else low_stock_products
        
        serializer =  ProductListSerializer(low_stock_products, many=True)
        return serializer.data

    '''
        {
        "summary": {
            "revenue": 245000,
            "orders": 124,
            "products": 38,
            "pending_orders": 9
        },

        "revenue_chart": [],

        "order_status": {
            "pending": 5,
            "processing": 8,
            "shipped": 12,
            "delivered": 90,
            "cancelled": 9
        },

        "recent_orders": [],

        "top_products": [],

        "low_stock_products": [],

        "latest_reviews": [],

        "notifications": []
    }
    
    '''