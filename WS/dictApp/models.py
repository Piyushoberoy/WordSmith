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
            self.synonyms = ", ".join(word.strip().capitalize()
                                      for word in self.synonyms.split(","))

        # Capitalize each antonym and join back as comma-separated
        if self.antonyms:
            self.antonyms = ", ".join(word.strip().capitalize()
                                      for word in self.antonyms.split(","))

        super().save(*args, **kwargs)

    def __str__(self):
        return self.word


class Idiom(models.Model):
    id = models.AutoField(primary_key=True)
    phrase = models.CharField(
        max_length=255, unique=True)  # Unique idiom phrase
    # Explanation of the idiom
    meaning = models.TextField(blank=True, null=True)
    # Example sentence using the idiom
    example = models.TextField(blank=True, null=True)
    insights = models.TextField(blank=True, null=True)  # AI-generated insights
    category = models.CharField(
        max_length=100, blank=True, null=True)  # Category of the idiom
    related_idioms = models.TextField(blank=True, null=True)  # Related idioms
    # Historical background of the idiom
    origin = models.TextField(blank=True, null=True)
    difficulty_level = models.CharField(
        max_length=20,
        choices=[('Beginner', 'Beginner'), ('Intermediate',
                                            'Intermediate'), ('Advanced', 'Advanced')],
        default='Beginner'
    )  # Difficulty Level
    tags = models.CharField(max_length=255, blank=True,
                            null=True)  # Tags for searchability
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )  # User who added the idiom
    created_at = models.DateTimeField(
        auto_now_add=True)  # Timestamp of creation

    def save(self, *args, **kwargs):
        """Ensure all text fields are properly formatted before saving."""

        # Capitalize the first letter of the phrase, meaning, example, and origin
        self.phrase = self.phrase.capitalize() if self.phrase else self.phrase
        self.meaning = self.meaning.capitalize() if self.meaning else self.meaning
        self.example = self.example.capitalize() if self.example else self.example
        self.origin = self.origin.capitalize() if self.origin else self.origin

        # Ensure insights start with a capital letter
        self.insights = self.insights.capitalize() if self.insights else self.insights

        # Capitalize each tag and join back as comma-separated values
        if self.tags:
            self.tags = ", ".join(tag.strip().capitalize()
                                  for tag in self.tags.split(","))

        # Capitalize the category
        if self.category:
            self.category = self.category.capitalize()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.phrase
