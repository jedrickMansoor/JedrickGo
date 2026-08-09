from django.contrib import admin
from apps.notification.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "recipient",
        "sender",
        "title",
        "is_read",
        "created_at",
    )

    list_filter = (
        "is_read",
        "created_at",
    )

    search_fields = (
        "title",
        "message",
        "recipient__user__username",
        "sender__user__username",
    )