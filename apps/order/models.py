from django.db import models
from apps.account.models import Account
from apps.product.models import Product

# ORDER
class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    shipping_address = models.TextField()

    phone_number = models.CharField(max_length=20)

    payment_method = models.CharField(max_length=30)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# SELLER ORDER
class SellerOrder(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="seller_orders"
    )

    seller = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="seller_orders",
        limit_choices_to={"user__role": "seller"}
    )

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discounted = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    status = models.CharField(
        max_length=20,
        choices=Order.STATUS_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



# ORDER ITEMS
class OrderItem(models.Model):
    seller_order = models.ForeignKey(
        SellerOrder,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="order_items"
    )

    quantity = models.PositiveIntegerField()

    original_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    
    final_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)