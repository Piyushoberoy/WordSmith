from django.db import models
from dictApp.models import Word
from userApp.models import CustomUser

# class Quiz(models.Model):
#     """Quiz containing multiple questions"""
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Quiz {self.id} by {self.user.username}"

# class Question(models.Model):
#     """Represents a question in a quiz"""
#     quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
#     word = models.ForeignKey(Word, on_delete=models.CASCADE)
#     question_text = models.TextField()
#     question_type = models.CharField(
#         max_length=10, 
#         choices=[("MCQ", "MCQ"), ("MSQ", "MSQ"), ("FIB", "Fill in the Blank")]
#     )

#     def __str__(self):
#         return f"Q: {self.question_text}"

# class Answer(models.Model):
#     """Stores answer choices for a question"""
#     question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
#     text = models.CharField(max_length=255)
#     is_correct = models.BooleanField(default=False)

#     def __str__(self):
#         return f"{self.text} ({'Correct' if self.is_correct else 'Wrong'})"

class MCQ(models.Model):
    id = models.AutoField(primary_key=True)
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='mcqs')
    question_text = models.TextField()
    option1 = models.CharField(max_length=255)
    option2 = models.CharField(max_length=255)
    option3 = models.CharField(max_length=255)
    option4 = models.CharField(max_length=255)
    correct_option = models.PositiveSmallIntegerField(choices=[(1, 'Option 1'), (2, 'Option 2'), (3, 'Option 3'), (4, 'Option 4')])
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"MCQ for {self.word}"


