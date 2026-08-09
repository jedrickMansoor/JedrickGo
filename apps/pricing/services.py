from decimal import Decimal
from django.utils import timezone

class PricingService:

    @staticmethod
    def calculate_product_price(product):
        original_price = product.price
        today = timezone.now().date()

        deal = product.deals.filter(
            status="active",
            start_date__lte=today,
            end_date__gte=today,
        ).order_by("-priority").first()

        if not deal:
            return {
                "original_price": original_price,
                "discount_amount": Decimal("0"),
                "final_price": original_price,
            }

        if deal.type == "percentage":
            discount_amount = (
                original_price * Decimal(deal.value) / Decimal("100")
            )
        else:
            discount_amount = Decimal(deal.value)

        final_price = max(
            Decimal("0"),
            original_price - discount_amount
        )

        return {
            "original_price": original_price,
            "discount_amount": discount_amount,
            "final_price": final_price,
        }

    @staticmethod
    def calculate_cart_item(product, quantity):
        prices = PricingService.calculate_product_price(product)

        original_price = prices["original_price"]
        discount_amount = prices["discount_amount"]
        final_price = prices["final_price"]

        return {
            "original_price": original_price * quantity,
            "discount_amount": discount_amount * quantity,
            "final_price": final_price * quantity,
        }


    @staticmethod
    def calculate_cart_prices(order):
        cart_items = order.items.all()

        total_original_price = sum(
            item.original_price for item in cart_items
        )
        total_discount_amount = sum(
            item.discount_amount for item in cart_items
        )
        total_final_price = sum(
            item.final_price for item in cart_items
        )

        return {
            "total_original_price": total_original_price,
            "total_discount_amount": total_discount_amount,
            "total_final_price": total_final_price,
        }
         
    @staticmethod
    def calculate_order_totals(order):
        ...

    @staticmethod
    def apply_coupon(total, coupon):
        ...