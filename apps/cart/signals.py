from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.account.models import Account
from .models import Cart


@receiver(post_save, sender=Account)
def create_cart(sender, instance, created, **kwargs):
    if created:
        Cart.objects.create(account=instance)