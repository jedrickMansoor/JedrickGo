from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from apps.account.models import Account
from apps.product.models import Product
from django.utils.text import slugify
from django.core.validators import RegexValidator

from cloudinary.models import CloudinaryField



class Deal(models.Model):

    DEAL_TYPES = [
        ("percentage", "Percentage"),
        ("fixed", "Fixed Amount"),
        ("free_shipping", "Free Shipping"),
        ("buy_x_get_y", "Buy X Get Y"),
    ]

    STATUSS = [
        ("draft", "Draft"),
        ("active", "Active"),
        ("expired", "Expired"),
        ("disabled", "Disabled"),
    ]
    
    CREATORS = [
        ("admin", "Admin"),
        ("seller", "Seller")
    ]
    
    slug = models.SlugField(unique=True, null=True, blank=True)
    
    products = models.ManyToManyField(
        "product.Product",
        related_name="deals",
        blank=True,
    )

    seller = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="deals",
        null=True,
        blank=True
    )

    title = models.CharField(max_length=100)

    description = models.TextField(
        blank=True,
        null=True
    )

    type = models.CharField(
        max_length=20,
        choices=DEAL_TYPES,
        default="percentage"
    )
    
    hex_color_validator = RegexValidator(
        regex=r"^#[0-9A-Fa-f]{6}$",
        message="Enter a valid hex color (e.g. #F8F9FA).",
    )
    
    color = models.CharField(
        max_length=7,
        default="#F8F9FA",
        blank=True,
        null=True,
        validators=[hex_color_validator],
    )
    
    creator_type = models.CharField(
        max_length=20,
        choices=CREATORS,
        default="seller",
        null=True,
        blank=True
    )

    value = models.PositiveIntegerField()

    start_date = models.DateField()
    end_date = models.DateField()

    status = models.CharField(
        max_length=10,
        choices=STATUSS,
        default="draft"
    )

    priority = models.PositiveSmallIntegerField(
        default=5,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ]
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.end_date < self.start_date:
            raise ValidationError(
                {"end_date": "End date cannot be before start date."}
            )
        if self.type == "percentage" and self.value > 100:
            raise ValidationError({
                "value": "Percentage discount cannot exceed 100."
            })

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        self.title = self.title.title()
        self.slug = slugify(self.title)
        super().save(*args, **kwargs) 


# DEAL IMAGE MODEL
class DealImage(models.Model):
    deal = models.OneToOneField(Deal, on_delete=models.CASCADE, related_name="image")
    image = CloudinaryField("image")
    
    def __str__(self):
        return f"Image for {self.product.name}"