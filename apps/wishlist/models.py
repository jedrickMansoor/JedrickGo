from django.db import models

from apps.account.models import Account
from apps.product.models import Product


class Wishlist(models.Model):
    account = models.OneToOneField(
        Account,
        on_delete=models.CASCADE,
        related_name='wishlist'
    )
    products = models.ManyToManyField(
        Product,
        related_name='wishlists',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Wishlist for {self.account}"
