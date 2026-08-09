from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.notification.models import Notification
from apps.notification.serializers import NotificationSerializer
from apps.account.models import Account
from django.db import transaction

from django.db.models import Q

from django.utils import timezone
from datetime import timedelta

# NOTIFICATION
class NotificationViewSet(ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        queryset = Notification.objects.filter(recipient=self.request.user.account).order_by('-created_at')
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(message__icontains=search)
            )
            
        status_filter = self.request.query_params.get("status")
        if status_filter:
            if status_filter not in ["read", "unread"]:
                return Response(
                    {"error": "Invalid status filter. Use 'read' or 'unread'."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if status_filter == "read":
                queryset = queryset.filter(is_read=True)
            else:
                queryset = queryset.filter(is_read=False)
        type_filter = self.request.query_params.get("type")
        if type_filter:
            queryset = queryset.filter(notification_type=type_filter)
        
        date_filter = self.request.query_params.get("date")
        
        if date_filter:        
            today = timezone.localdate()
    
            if date_filter == "today":
                queryset = queryset.filter(created_at__date=today)

            elif date_filter == "yesterday":
                queryset = queryset.filter(
                    created_at__date=today - timedelta(days=1)
                )

            elif date_filter == "this_week":
                start_of_week = today - timedelta(days=today.weekday())
                queryset = queryset.filter(created_at__date__gte=start_of_week)

            elif date_filter == "this_month":
                queryset = queryset.filter(
                    created_at__year=today.year,
                    created_at__month=today.month,
                )
            
        return queryset


    # CREATE NOTIFICATION
    def create(self, request, *args, **kwargs):
        create_for = request.query_params.get("createFor")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if create_for == "system":
            recipients = Account.objects.exclude(
                user__role="admin"
            )

        elif create_for == "customers":
            recipients = Account.objects.filter(
                user__role="customer"
            )

        else:
            return Response(
                {
                    "detail": "Invalid createFor value. Use 'system' or 'customers'."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            notifications = [
                Notification(
                    sender=request.user.account,   
                    recipient=recipient,           
                    title=serializer.validated_data["title"],
                    message=serializer.validated_data["message"],
                    notification_type=serializer.validated_data["notification_type"],
                    content_type=serializer.validated_data.get("content_type"),
                    object_id=serializer.validated_data.get("object_id"),
                )
                for recipient in recipients
            ]

            Notification.objects.bulk_create(notifications)

        return Response(
            {
                "message": f"{len(notifications)} notifications created successfully."
            },
            status=status.HTTP_201_CREATED,
        )

    # GET AND UPDATE NOTIFICATION
    @action(detail=False, methods=['get', 'patch'])
    def me(self, request):
        notification, _ = Notification.objects.get_or_create(account=request.user.account)

        if request.method == 'GET':
            serializer = self.get_serializer(notification)
            return Response(serializer.data)

        serializer = self.get_serializer(
            notification,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)
    
    # UNCREAD NOTIFICATION
    @action(detail=False, methods=["get"], url_path="unread-count")
    def unread_notifications(self, request):
        unread_count = Notification.objects.filter(
            recipient=request.user.account,
            is_read=False
        ).count()

        return Response(
            {
                "unread_count": unread_count
            },
            status=status.HTTP_200_OK
        )

    # READ ALL
    @action(detail=False, methods=["patch"], url_path="mark-all-read")
    def mark_all_read(self, request):
        updated = Notification.objects.filter(
            recipient=request.user.account,
            is_read=False
        ).update(is_read=True)

        return Response(
            {
                "message": f"{updated} notifications marked as read."
            },
            status=status.HTTP_200_OK
        )