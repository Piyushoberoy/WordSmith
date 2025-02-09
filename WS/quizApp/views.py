from django.shortcuts import render
from .models import MCQ

def quiz_list(request):
    quizzes = MCQ.objects.all()
    return render(request, 'quizApp/quizList.html', {'quizzes': quizzes})