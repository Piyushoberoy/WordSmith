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

    def save(self, *args, **kwargs):
        """Ensure all text fields are properly formatted before saving."""
        self.word = self.word.capitalize() if self.word else self.word
        self.meaning = self.meaning.capitalize() if self.meaning else self.meaning
        self.example = self.example.capitalize() if self.example else self.example

        # Capitalize each synonym and join back as comma-separated
        if self.synonyms:
            self.synonyms = ", ".join(word.strip().capitalize() for word in self.synonyms.split(","))

        # Capitalize each antonym and join back as comma-separated
        if self.antonyms:
            self.antonyms = ", ".join(word.strip().capitalize() for word in self.antonyms.split(","))

        super().save(*args, **kwargs)

    def __str__(self):
        return self.word
