from apps.order.models import Order, SellerOrder

def update_order_status(order):
    
    seller_orders = SellerOrder.objects.filter(order=order)
    
    if not seller_orders.exists():
        return
    
    order_status_final = ""

    for order in seller_orders:
        if order.status == "delivered":
            order_status_final = "delivered"

        elif order.status == "shipped":
            if order_status_final != "delivered":
                order_status_final = "shipped"

        elif order.status == "processing":
            if order_status_final not in ["delivered", "shipped"]:
                order_status_final = "processing"
        elif order.status == "confirmed":
            if order_status_final not in ["delivered", "shipped", "processing"]:
                order_status_final = "confirmed"
        elif order.status == "pending":
            if order_status_final not in ["delivered", "shipped", "processing", "confirmed"]:
                order_status_final = "pending"
        elif order.status == "cancelled":
            if order_status_final not in ["delivered", "shipped", "processing", "confirmed", "pending"]:
                order_status_final = "cancelled"

    order.status = order_status_final
    order.save()