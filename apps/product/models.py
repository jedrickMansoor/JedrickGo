from django.db import models
from apps.product_category.models import ProductCategory
from apps.user.models import User
from apps.account.models import Account
from apps.brand.models import Brand
from apps.collection.models import Collection

from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from cloudinary.models import CloudinaryField



# Create your models here.
class Product(models.Model):
    seller = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="products")
    category = models.ForeignKey(ProductCategory, on_delete=models.PROTECT, related_name="products")
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name="products", null=True, blank=True)
    collection = models.ForeignKey(Collection, on_delete=models.PROTECT, related_name="products", null=True, blank=True)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.name = self.name.title()
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)   


# PRODUCT IMAGE MODEL
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = CloudinaryField("image")
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.product.name}"
    
# PRODUCT REVIEW MODEL
class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="reviews", null=True, blank=True)
    rating = models.DecimalField(
    max_digits=2,      
    decimal_places=1,  
    validators=[
        MinValueValidator(1.0),
        MaxValueValidator(5.0),
    ]
)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} for {self.product.name}"    