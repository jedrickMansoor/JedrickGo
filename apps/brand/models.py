from django.db import models
from django.utils.text import slugify
from cloudinary.models import CloudinaryField
from apps.product_category.models import ProductCategory


class Brand(models.Model):
    category = models.ForeignKey(ProductCategory, models.CASCADE, related_name="brands", null=True, blank=True)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    logo = CloudinaryField("image", blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = self.name.title()
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        lookup_field = "slug"
         
        