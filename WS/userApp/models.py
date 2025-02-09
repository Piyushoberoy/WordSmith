from django.contrib.auth.models import AbstractUser
from django.db import models

# class CustomUser(AbstractUser):
#     # Add related_name for both fields to avoid clashes with the default User model
#     groups = models.ManyToManyField(
#         'auth.Group', 
#         related_name='customuser_set',  # Change this to whatever name you prefer
#         blank=True
#     )
#     user_permissions = models.ManyToManyField(
#         'auth.Permission', 
#         related_name='customuser_set',  # Change this as well
#         blank=True
#     )

class CustomUser(AbstractUser):
    """Custom user model extending Django's default user"""
    email = models.EmailField(unique=True)
    is_premium = models.BooleanField(default=False)

    # Resolve conflicts by adding unique related_name values
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="customuser_set",
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="customuser_set",
        blank=True,
    )

    def __str__(self):
        return self.username

