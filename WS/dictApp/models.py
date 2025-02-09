from django.conf import settings
from django.db import models

class Word(models.Model):
    word = models.CharField(max_length=255, unique=True)
    meaning = models.TextField(blank=True, null=True)
    synonyms = models.TextField(blank=True, null=True)
    antonyms = models.TextField(blank=True, null=True)
    example = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        null=True,  # Allow null values to prevent errors
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.word
