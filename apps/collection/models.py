from django.db import models
from django.utils.text import slugify
from cloudinary.models import CloudinaryField
from apps.product_category.models import ProductCategory
from apps.account.models import Account

class Collection(models.Model):
    CREATOR_CHOICES = (
        ("admin", "Admin"),
        ("seller", "Seller"),
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    creator_type = models.CharField(max_length=10, choices=CREATOR_CHOICES)
    seller = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    
    
    def __str__(self):
            return self.name
    
    def save(self, *args, **kwargs):
        self.name = self.name.title()
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)