from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.shortcuts import render, redirect
from quizApp.models import *
from dictApp.models import *
import json

CustomUser = get_user_model()  # Get the custom user model dynamically

def register(request):
    if request.user.is_authenticated:  # Prevent logged-in users from accessing the register page
        return redirect('home')

    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            if CustomUser.objects.filter(username=username).exists():
                messages.error(request, "Username already taken")
            elif CustomUser.objects.filter(email=email).exists():
                messages.error(request, "Email already in use")
            else:
                # Create a new CustomUser instance
                user = CustomUser.objects.create_user(username=username, email=email, password=password1)
                user.save()
                login(request, user)
                messages.success(request, "Registration successful!")
                return redirect('home')
        else:
            messages.error(request, "Passwords do not match")

    return render(request, 'userApp/register.html')

def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            next_url = request.GET.get("next", "/")
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'userApp/login.html')

def user_logout(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('home')

def dashboard(request):
    user = request.user

    # Fetch total words added by user
    total_words = Word.objects.filter(created_by=user).count()

    # Fetch total MCQs created by user
    total_mcqs = MCQ.objects.filter(created_by=user).count()

    # Fetch total words learned (Assuming correct answers count as learned)
    total_words_learned = QuizAttempt.objects.filter(user=user, score__gte=3).count()

    # Fetch quiz performance
    quizzes = QuizAttempt.objects.filter(user=user).order_by("date_attempted")
    quiz_dates = [q.date_attempted.strftime("%Y-%m-%d") for q in quizzes]
    quiz_scores = [q.score for q in quizzes]

    # Learning progress (Cumulative score over time)
    learning_dates = quiz_dates
    learning_progress = [sum(quiz_scores[:i+1]) for i in range(len(quiz_scores))]

    context = {
    "total_words": total_words,
    "total_mcqs": total_mcqs,
    "total_words_learned": total_words_learned,
    "quiz_dates": json.dumps(quiz_dates),  # Convert lists to proper JSON
    "quiz_scores": json.dumps(quiz_scores),
    "learning_dates": json.dumps(learning_dates),
    "learning_progress": json.dumps(learning_progress),
}
    print(context)

    return render(request, "userApp/dashboard.html", context)

