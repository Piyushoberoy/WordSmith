from django.urls import path
from .views import *

urlpatterns = [
    path('', quiz_list, name='quiz_list'),
    path("save-attempt/", save_quiz_attempt, name="save_quiz_attempt"),
    path('filter-quizzes/', filter_quizzes, name='filter_quizzes'),
]