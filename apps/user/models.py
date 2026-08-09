from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(
        unique=True,
        max_length=255
    )

    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )
    
    role = models.CharField(
        max_length=20,
        choices=(
            ("customer", "Customer"),
            ("seller", "Seller"),
            ("admin", "Admin"),
        ),
        default="customer",
        blank=True,
        null=True   
    )

    is_active = models.BooleanField(default=True)

    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    objects = UserManager()

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email