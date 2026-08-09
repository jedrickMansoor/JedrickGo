from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User
from apps.account.models import Account
from apps.wishlist.models import Wishlist


@receiver(post_save, sender=User)
def create_account(sender, instance, created, **kwargs):
    if created:
        Account.objects.get_or_create(user=instance)

@receiver(post_save, sender=Account)
def create_wishlist(sender, instance, created, **kwargs):
    if created:
        Wishlist.objects.get_or_create(account=instance)

