from django.contrib.auth.models import AbstractUser
from django.db import models

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

    def save(self, *args, **kwargs):
        """Ensure username and email are stored in lowercase."""
        self.username = self.username.lower() if self.username else self.username
        self.email = self.email.lower() if self.email else self.email
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
