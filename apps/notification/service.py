import json
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from apps.account.models import Account
from .models import Notification
from apps.user.models import User

import logging
from firebase_admin import messaging
from .models import FCMDevice


class NotificationService:
    
    @staticmethod
    def send_push_notification(account, title, body, extra_data=None):
            devices = FCMDevice.objects.filter(account=account, is_active=True)
            tokens = list(devices.values_list('fcm_token', flat=True))
    
            if not tokens:
                return 0
    
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data={k: str(v) for k, v in (extra_data or {}).items()},
                tokens=tokens,
            )
    
            response = messaging.send_each_for_multicast(message)
    
            # Clean up deactivated tokens
            failed_tokens = []
            for idx, resp in enumerate(response.responses):
                if not resp.success:
                    err_code = resp.exception.code if resp.exception else None
                    if err_code in ['UNREGISTERED', 'INVALID_ARGUMENT']:
                        failed_tokens.append(tokens[idx])
    
            if failed_tokens:
                FCMDevice.objects.filter(fcm_token__in=failed_tokens).update(is_active=False)
    
            return response.success_count

    @staticmethod
    def send(
        *,
        recipient,
        title,
        message,
        sender=None,
        target=None,
        notification_type="system",
    ):
        # Create notification
        notification = Notification.objects.create(
            recipient=recipient,
            sender=sender,
            notification_type=notification_type,
            title=title,
            message=message,
            target=target,
        )

        # Channel Layer
        channel_layer = get_channel_layer()
        
        group_name = f"user_{recipient.id}"
        print(f"Sending to: {recipient.first_name}")
        print(f"Sending to group: {group_name}")

        # Send WebSocket event
        async_to_sync(channel_layer.group_send)(
            f"user_{recipient.id}",
            {
                "type": "send_notification",
                "notification": {
                    "id": notification.id,
                    "type": notification.notification_type,
                    "title": notification.title,
                    "message": notification.message,
                    "is_read": notification.is_read,
                    "created_at": notification.created_at.isoformat(),
                },
            },
        )
        
        # Fetches the first record or returns None without throwing an exception
        recipient_user = User.objects.filter(id=recipient.id).first()

        if recipient_user:
            try:
                NotificationService.send_push_notification(
                    account=recipient_user.account, 
                    title=title, 
                    body=message
                )
            except Exception as e:
                print(f"Failed to send push notification: {str(e)}")
        else:
            print(f"No account found for user {recipient}.")

        return notification

    @staticmethod
    def send_to_customers(
        *,
        title,
        message,
        sender=None,
        target=None,
        notification_type="system",
    ):

        customers = Account.objects.filter(
            user__role="customer"
        )

        for customer in customers:
            NotificationService.send(
                recipient=customer,
                sender=sender,
                title=title,
                message=message,
                target=target,
                notification_type=notification_type,
            )

    @staticmethod
    def send_to_non_admins(
        *,
        title,
        message,
        sender=None,
        target=None,
        notification_type="system",
    ):

        users = Account.objects.exclude(
            user__role="admin"
        )

        for user in users:
            NotificationService.send(
                recipient=user,
                sender=sender,
                title=title,
                message=message,
                target=target,
                notification_type=notification_type,
            )
    
    @staticmethod
    def send_to_sellers(
        *,
        title,
        message,
        sender=None,
        target=None,
        notification_type="system",
    ):

        sellers = Account.objects.filter(
            user__role="seller"
        )

        for seller in sellers:
            NotificationService.send(
                recipient=seller,
                sender=sender,
                title=title,
                message=message,
                target=target,
                notification_type=notification_type,
            )
    
    @staticmethod
    def get_order_notification(status):
        notifications = {
            "pending": {
                "notification_type": "order_created",
                "title": "New Order Created",
                "message": "An order has been created.",
            },
            "confirmed": {
                "notification_type": "order_confirmed",
                "title": "Order Confirmed",
                "message": "Your order has been confirmed.",
            },
            "processing": {
                "notification_type": "order_confirmed",
                "title": "Order Processing",
                "message": "Your order is now being processed.",
            },
            "shipped": {
                "notification_type": "order_shipped",
                "title": "Order Shipped",
                "message": "Your order has been shipped.",
            },
            "delivered": {
                "notification_type": "order_delivered",
                "title": "Order Delivered",
                "message": "Your order has been delivered.",
            },
            "cancelled": {
                "notification_type": "order_cancelled",
                "title": "Order Cancelled",
                "message": "Your order has been cancelled.",
            },
        }

        return notifications.get(
            status,
            {
                "notification_type": "system",
                "title": "Order Update",
                "message": "Your order status has been updated.",
            },
        )
    
    
        
        