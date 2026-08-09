from django.db import models
from apps.user.models import User
from cloudinary.models import CloudinaryField

# Create your models here.
class Account(models.Model):
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="account"
    )

    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)

    phone_number = models.CharField(max_length=20, null=True, blank=True)

    profile_picture = CloudinaryField("image")

    date_of_birth = models.DateField(
        blank=True,
        null=True
    )
    gender = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"