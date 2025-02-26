import json
from quizApp.models import *
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, get_user_model

CustomUser = get_user_model()  # Get the custom user model dynamically

def register(request):
    if request.user.is_authenticated:
        print("[INFO] User is already authenticated, redirecting to home.")
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        if not username or not email or not password1 or not password2:
            messages.error(request, "All fields are required")
            print("[WARNING] Registration failed - Missing required fields.")
            return render(request, 'userApp/register.html')

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            print("[WARNING] Registration failed - Passwords do not match.")
            return render(request, 'userApp/register.html')

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            print(f"[WARNING] Registration failed - Username '{username}' already exists.")
        elif CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already in use")
            print(f"[WARNING] Registration failed - Email '{email}' is already registered.")
        else:
            try:
                user = CustomUser.objects.create_user(username=username, email=email, password=password1)
                user.save()
                login(request, user)
                messages.success(request, "Registration successful!")
                print(f"[INFO] User registered successfully - Username: {username}, Email: {email}")
                return redirect('home')
            except Exception as e:
                print(f"[ERROR] Failed to register user '{username}' - {e}")
                messages.error(request, "An error occurred. Please try again.")

    return render(request, 'userApp/register.html')

def user_login(request):
    if request.user.is_authenticated:
        print("[INFO] User is already authenticated, redirecting to home.")
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not username or not password:
            messages.error(request, "Username and password are required")
            print("[WARNING] Login failed - Username or password missing.")
            return render(request, 'userApp/login.html')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            print(f"[INFO] User logged in successfully - Username: {user.username}")
            next_url = request.GET.get("next", "/")
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password")
            print(f"[ERROR] Login failed - User '{username}' does not exist or incorrect password.")

    return render(request, 'userApp/login.html')

def user_logout(request):
    print(f"[INFO] User '{request.user.username}' is logging out.")
    logout(request)
    messages.success(request, "You have successfully logged out.")
    print("[INFO] User logged out successfully.")
    return redirect('home')

def dashboard(request):
    user = request.user

    if not user.is_authenticated:
        print("[WARNING] Unauthorized access attempt to dashboard.")
        messages.error(request, "You need to log in to access the dashboard.")
        return redirect('user_login')

    print(f"[INFO] Fetching dashboard data for user: {user.username}")

    # Fetch total words added by user
    total_words = Word.objects.filter(created_by=user).count()
    print(f"[INFO] Total words added by user: {total_words}")

    # Fetch total MCQs created by user
    total_mcqs = MCQ.objects.filter(created_by=user).count()
    print(f"[INFO] Total MCQs created by user: {total_mcqs}")

    # Fetch total words learned (Assuming correct answers count as learned)
    total_words_learned = QuizAttempt.objects.filter(user=user, score__gte=3).count()
    print(f"[INFO] Total words learned by user: {total_words_learned}")

    # Fetch quiz performance
    quizzes = QuizAttempt.objects.filter(user=user).order_by("date_attempted")
    
    if quizzes.exists():
        quiz_dates = [q.date_attempted.strftime("%Y-%m-%d") for q in quizzes]
        quiz_scores = [q.score for q in quizzes]

        # Learning progress (Cumulative score over time)
        learning_progress = [sum(quiz_scores[:i+1]) for i in range(len(quiz_scores))]

        print(f"[INFO] Quiz data fetched for user: {user.username}")
        print(f"[INFO] Quiz dates: {quiz_dates}")
        print(f"[INFO] Quiz scores: {quiz_scores}")
        print(f"[INFO] Learning progress: {learning_progress}")
    else:
        quiz_dates = []
        quiz_scores = []
        learning_progress = []
        print(f"[WARNING] No quiz data found for user: {user.username}")

    context = {
        "total_words": total_words,
        "total_mcqs": total_mcqs,
        "total_words_learned": total_words_learned,
        "quiz_dates": json.dumps(quiz_dates),  # Convert lists to JSON for frontend
        "quiz_scores": json.dumps(quiz_scores),
        "learning_dates": json.dumps(quiz_dates),
        "learning_progress": json.dumps(learning_progress),
    }

    print("[INFO] Dashboard data prepared successfully.")
    
    return render(request, "userApp/dashboard.html", context)