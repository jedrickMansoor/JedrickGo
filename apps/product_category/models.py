from pyclbr import Class
from django.db import models
from django.utils.text import slugify
from cloudinary.models import CloudinaryField



# Create your models here.
class ProductCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)
    image = CloudinaryField("image", blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = self.name.title()
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)