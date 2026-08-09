from django.contrib import admin

from apps.payment.models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'amount', 'status', 'payment_method', 'transaction_id', 'created_at')
    list_filter = ('status', 'payment_method')
    search_fields = ('transaction_id',)
