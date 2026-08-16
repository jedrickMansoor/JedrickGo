from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from apps.account.models import Account
from django.conf import settings


class Notification(models.Model):
    
    NOTIFICATION_TYPES = (
        ("new_product", "New Product"),
        
        ("new_deal", "New Deal"),
        ("new_collection", "New Collection"),
        ("new_brand", "New Brand"),

        ("new_message", "New Message"),

        ("order_created", "Order Created"),
        ("order_confirmed", "Order Confirmed"),
        ("order_shipped", "Order Shipped"),
        ("order_delivered", "Order Delivered"),
        ("order_cancelled", "Order Cancelled"),
        

        ("payment_success", "Payment Success"),
        ("payment_failed", "Payment Failed"),
        ("payment_refunded", "Payment Refunded"),

        ("wishlist_price_drop", "Wishlist Price Drop"),
        ("wishlist_back_in_stock", "Wishlist Back In Stock"),

        ("system", "System"),
    )
    
    

    recipient = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="received_notifications",
        null=True,
        blank=True,
    )

    sender = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="sent_notifications",
        null=True,
        blank=True,
    )
    
    notification_type = models.CharField(max_length=40,
        choices=NOTIFICATION_TYPES,
        default="system",
        null = True,
        blank=True
    )
    

    title = models.CharField(max_length=255)

    message = models.TextField()

    is_read = models.BooleanField(default=False)

    # Generic Relation
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    object_id = models.PositiveBigIntegerField(
        null=True,
        blank=True,
    )

    target = GenericForeignKey(
        "content_type",
        "object_id"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self):
        return f"{self.recipient} - {self.title}"


# FCM DEVICES
class FCMDevice(models.Model):
    PLATFORM_CHOICES = (
        ("android", "Android"),
        ("ios", "iOS"),
        ("web", "Web"),
    )

    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="fcm_devices",
        null=True,
        blank=True,
    )
    fcm_token = models.TextField(unique=True, db_index=True)
    device_id = models.CharField(max_length=255, blank=True, null=True)
    platform = models.CharField(
        max_length=10, choices=PLATFORM_CHOICES, default="android"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["account", "is_active"]),
        ]

    def __str__(self):
        return f"{self.account} - {self.platform} ({self.fcm_token[:10]}...)"