import json
import random
from .models import MCQ
from django.shortcuts import render
from django.http import JsonResponse
from userApp.models import CustomUser
from dictApp.models import Word, Idiom
from .utils import generate_mcq, generate_idiom_mcq
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from quizApp.models import QuizAttempt, MCQ, IdiomMCQ
from django.contrib.auth.decorators import login_required

@login_required
def create_mcq(request, word):
    print("[INFO] MCQ creation started...")

    try:
        # Ensure user is authenticated
        if not request.user.is_authenticated:
            print("[ERROR] User not authenticated.")
            return JsonResponse({"error": "User not authenticated."}, status=403)

        print(f"[INFO] Looking for word: {word.lower()}")
        
        # Fetch the word instance from the database
        try:
            word_instance = Word.objects.get(word__iexact=word.lower())
            print(f"[INFO] Found word: {word_instance.word}")
        except Word.DoesNotExist:
            print("[ERROR] Word not found in the database.")
            return JsonResponse({"error": "Word not found."}, status=404)

        # Generate MCQs
        print("[INFO] Generating MCQs...")
        mcqs = generate_mcq(word_instance.word)

        if not mcqs:
            print("[ERROR] Failed to generate MCQs.")
            return JsonResponse({"error": "Could not generate MCQs."}, status=400)

        # Loop through each MCQ and save it
        for i, mcq in enumerate(mcqs):
            question, correct_answer, wrong1, wrong2, wrong3 = (
                mcq["question"], mcq["options"][0], mcq["options"][1], mcq["options"][2], mcq["options"][3]
            )

            if question == "Error retrieving details.":
                print("[ERROR] Could not generate valid MCQ.")
                return JsonResponse({"error": "Could not generate MCQ."}, status=400)

            print(f"[DEBUG] Generated Question {i+1}: {question}")

            # Shuffle options and determine correct index
            options = [correct_answer, wrong1, wrong2, wrong3]
            random.shuffle(options)
            correct_option = options.index(correct_answer) + 1  # 1-based index

            print(f"[DEBUG] Shuffled Options: {options}")
            print(f"[DEBUG] Correct Option Index: {correct_option}")

            # Ensure the user exists in CustomUser model
            user_exists = CustomUser.objects.filter(id=request.user.id).exists()
            print(f"[DEBUG] User Exists: {user_exists}")

            if not user_exists:
                print("[ERROR] User does not exist in CustomUser model.")
                return JsonResponse({"error": "User not found."}, status=500)

            # Save MCQ to the database
            mcq_instance = MCQ.objects.create(
                word=word_instance,
                question_text=question,
                option1=options[0],
                option2=options[1],
                option3=options[2],
                option4=options[3],
                correct_option=correct_option,
                created_by=request.user
            )
            print(f"[INFO] MCQ-{i+1} created successfully!")

        print("[SUCCESS] All MCQs generated and saved successfully! 🎉")
        return JsonResponse({"message": "MCQs created successfully."}, status=200)

    except Exception as e:
        print(f"[ERROR] Unexpected error while creating MCQs: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)

@login_required
def create_idiom_mcq(request, phrase):
    print("[INFO] Idiom MCQ creation started...")

    try:
        # Ensure user is authenticated
        if not request.user.is_authenticated:
            print("[ERROR] User not authenticated.")
            return JsonResponse({"error": "User not authenticated."}, status=403)

        print(f"[INFO] Looking for idiom: {phrase.lower()}")

        # Fetch the idiom from the database
        try:
            idiom_instance = Idiom.objects.get(phrase__iexact=phrase.lower())
            print(f"[INFO] Found idiom: {idiom_instance.phrase}")
        except Idiom.DoesNotExist:
            print("[ERROR] Idiom not found in the database.")
            return JsonResponse({"error": "Idiom not found."}, status=404)

        # Generate MCQs
        print("[INFO] Generating MCQs...")
        mcqs = generate_idiom_mcq(idiom_instance.phrase)

        if not mcqs:
            print("[ERROR] Failed to generate MCQs.")
            return JsonResponse({"error": "Could not generate MCQs."}, status=400)

        # Loop through and save each MCQ
        for i, mcq in enumerate(mcqs):
            question, correct_answer, wrong1, wrong2, wrong3 = (
                mcq["question"], mcq["options"][0], mcq["options"][1], mcq["options"][2], mcq["options"][3]
            )

            if question == "Error retrieving details.":
                print("[ERROR] Could not generate a valid MCQ.")
                return JsonResponse({"error": "Could not generate MCQ."}, status=400)

            print(f"[DEBUG] Generated Question {i+1}: {question}")

            # Shuffle options and determine the correct index
            options = [correct_answer, wrong1, wrong2, wrong3]
            random.shuffle(options)
            correct_option = options.index(correct_answer) + 1  # 1-based index

            print(f"[DEBUG] Shuffled Options: {options}")
            print(f"[DEBUG] Correct Option Index: {correct_option}")

            # Ensure the user exists in CustomUser model
            user_exists = CustomUser.objects.filter(id=request.user.id).exists()
            print(f"[DEBUG] User Exists: {user_exists}")

            if not user_exists:
                print("[ERROR] User does not exist in CustomUser model.")
                return JsonResponse({"error": "User not found."}, status=500)

            # Save MCQ to the database
            mcq_instance = IdiomMCQ.objects.create(
                idiom=idiom_instance,
                question_text=question,
                option1=options[0],
                option2=options[1],
                option3=options[2],
                option4=options[3],
                correct_option=correct_option,
                created_by=request.user
            )
            print(f"[INFO] MCQ-{i+1} created successfully!")

        print("[SUCCESS] All MCQs generated and saved successfully! 🎉")
        return JsonResponse({"message": "MCQs created successfully."}, status=200)

    except Exception as e:
        print(f"[ERROR] Unexpected error while creating MCQs: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)

@login_required
def quiz_list(request):
    print("[INFO] Fetching quiz list...")

    try:
        # Retrieve all MCQs
        quizzes = MCQ.objects.filter(created_by=request.user)
        print(f"[DEBUG] Total quizzes retrieved: {quizzes.count()}")

        # Retrieve distinct words related to MCQs
        words = quizzes.select_related('word').values_list('word__word', flat=True).distinct()
        print(f"[DEBUG] Total unique words retrieved: {len(words)}")

        # Render the template with quizzes and words
        return render(request, 'quizApp/quizList.html', {
            'quizzes': quizzes,
            'words': words
        })

    except Exception as e:
        print(f"[ERROR] Unexpected error while fetching quizzes: {str(e)}")
        return render(request, 'quizApp/quizList.html', {
            'quizzes': [],
            'words': [],
            'error': "An error occurred while retrieving quizzes."
        })

# @csrf_exempt  # Remove if using CSRF protection
# def save_quiz_attempt(request):
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)  # Parse JSON

#             print("Received Data:", data)  # Debugging print statement

#             attempts = data.get("attempts", [])
#             user = request.user  # Ensure the user is authenticated

#             for attempt in attempts:
#                 mcq_id = attempt.get("mcq_id")
#                 selected_option = int(attempt.get("selected_option"))
                
#                 mcq = MCQ.objects.get(id=mcq_id)  # Fetch MCQ from DB
#                 is_correct = (mcq.correct_option == selected_option)
#                 score = 1 if is_correct else 0  # Assign score

#                 # Save attempt in database
#                 QuizAttempt.objects.create(
#                     user=user, mcq=mcq, score=score
#                 )

#             return JsonResponse({"message": "All attempts saved successfully!"}, status=200)

#         except Exception as e:
#             print("Error:", str(e))  # Print error message
#             return JsonResponse({"error": str(e)}, status=400)
    
#     return JsonResponse({"error": "Invalid request"}, status=405)
@csrf_exempt
@login_required
def save_quiz_attempt(request):
    if request.method == "POST":
        print("[INFO] Received quiz attempt submission.")

        try:
            data = json.loads(request.body)
            print("[DEBUG] Request Data:", data)

            # Extract data
            total_score = data.get("total_score", 0)
            max_score = data.get("max_score", 0)
            total_questions = data.get("total_questions", 0)
            selected_word = data.get("selected_word", "").strip()

            # Check user authentication
            user = request.user if request.user.is_authenticated else None
            if not user:
                print("[ERROR] Unauthorized access attempt.")
                return JsonResponse({"error": "User not authenticated"}, status=401)

            # Fetch Word object if a specific word is selected
            word = None
            if selected_word.upper() != "ALL" and selected_word:
                word = Word.objects.filter(word__iexact=selected_word, created_by = user).first()
                if not word:
                    print(f"[ERROR] Word '{selected_word}' not found.")
                    return JsonResponse({"error": "Selected word not found"}, status=400)

            # Save quiz attempt
            QuizAttempt.objects.create(
                user=user, 
                word=word, 
                score=total_score, 
                maxScore=max_score
            )
            print("[INFO] Quiz attempt saved successfully.")

            return JsonResponse({
                "message": "Quiz attempt saved successfully",
                "score": total_score
            })

        except json.JSONDecodeError:
            print("[ERROR] Invalid JSON data received.")
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

        except Exception as e:
            print(f"[ERROR] Unexpected error: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)

    print("[ERROR] Invalid request method.")
    return JsonResponse({"error": "Invalid request"}, status=400)

def filter_quizzes(request):
    print("[INFO] Received request to filter quizzes.")

    try:
        selected_word = request.GET.get('word', 'All').strip()
        user = request.user
        print(f"[DEBUG] Selected word: {selected_word}")

        # Filter quizzes based on selected word
        if selected_word.lower() != 'all':
            quizzes = MCQ.objects.filter(word__word__iexact=selected_word, created_by=user)
            print(f"[INFO] Found {quizzes.count()} quizzes for word '{selected_word}'.")
        else:
            quizzes = MCQ.objects.filter(created_by=user)
            print(f"[INFO] Showing all {quizzes.count()} quizzes.")

        # Render the filtered quizzes as HTML
        filtered_quizzes_html = render_to_string('quizApp/quizCard.html', {'quizzes': quizzes})
        print("[INFO] Rendered quiz cards successfully.")

        return JsonResponse({'filtered_quizzes_html': filtered_quizzes_html})

    except Exception as e:
        print(f"[ERROR] Unexpected error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)