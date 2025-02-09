from django.db import models
from dictApp.models import Word
from userApp.models import CustomUser

class MCQ(models.Model):
    id = models.AutoField(primary_key=True)
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='mcqs')
    question_text = models.TextField()
    option1 = models.CharField(max_length=255)
    option2 = models.CharField(max_length=255)
    option3 = models.CharField(max_length=255)
    option4 = models.CharField(max_length=255)
    correct_option = models.PositiveSmallIntegerField(
        choices=[(1, 'Option 1'), (2, 'Option 2'), (3, 'Option 3'), (4, 'Option 4')]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        """Ensure all text fields are capitalized."""
        self.question_text = self.question_text.capitalize() if self.question_text else self.question_text
        self.option1 = self.option1.capitalize() if self.option1 else self.option1
        self.option2 = self.option2.capitalize() if self.option2 else self.option2
        self.option3 = self.option3.capitalize() if self.option3 else self.option3
        self.option4 = self.option4.capitalize() if self.option4 else self.option4

        # Ensure correct_option is valid
        if self.correct_option not in [1, 2, 3, 4]:
            raise ValueError("Invalid correct option. Must be between 1 and 4.")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"MCQ for {self.word}"
