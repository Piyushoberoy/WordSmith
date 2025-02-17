import json
import random
from .models import MCQ
from .utils import generate_mcq
from dictApp.models import Word
from django.shortcuts import render
from django.http import JsonResponse
from userApp.models import CustomUser
from quizApp.models import QuizAttempt, MCQ
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string


def create_mcq(request, word):
    print("MCQ creation started...")

    try:
        if not request.user.is_authenticated:
            return JsonResponse({"error": "User not authenticated."}, status=403)

        print(f"Looking for word: {word.lower()}")
        word_instance = Word.objects.get(word__iexact=word.lower())
        print(f"Found word: {word_instance.word}")

        # Generate MCQ
        mcqs = generate_mcq(word_instance.word)
        # question, correct_answer, wrong1, wrong2, wrong3 = generate_mcq(word_instance.word)
        i = 0
        for mcq in mcqs:
            question, correct_answer, wrong1, wrong2, wrong3 = mcq["question"], mcq["options"][0], mcq["options"][1], mcq["options"][2], mcq["options"][3]
            if question == "Error retrieving details.":
                return JsonResponse({"error": "Could not generate MCQ."}, status=400)

            print(f"Generated Question: {question}")

            # Shuffle options and randomly assign the correct option
            options = [correct_answer, wrong1, wrong2, wrong3]
            random.shuffle(options)
            correct_option = options.index(correct_answer) + 1  # Get the correct option index (1-4)

            print(f"Shuffled Options: {options}")
            print(f"Correct Option Index: {correct_option}")

            # Debugging user before creation
            print(f"User: {request.user}")
            print(f"User Exists: {CustomUser.objects.filter(id=request.user.id).exists()}")

            # Store MCQ in database
            mcq = MCQ.objects.create(
                word=word_instance,
                question_text=question,
                option1=options[0],
                option2=options[1],
                option3=options[2],
                option4=options[3],
                correct_option=correct_option,  # Store randomly assigned correct option
                created_by=request.user
            )
            print(f"MCQ-{i+1} created successfully!")
            i += 1
        print("All MCQs generated and saved successfully!😊")

        return JsonResponse({"message": "MCQ created successfully.", "mcq_id": mcq.id}, status = 200)

    except Word.DoesNotExist:
        return JsonResponse({"error": "Word not found."}, status=404)
    except Exception as e:
        print("Error creating MCQ:", str(e))
        return JsonResponse({"error": str(e)}, status=500)

@login_required
def quiz_list(request):
    # Fetch the quizzes and any other data you need
    quizzes = MCQ.objects.all()  # Modify this query as needed
    words = MCQ.objects.select_related('word').values_list('word__word', flat=True).distinct()
    
    # Pass the quizzes and words to the template context
    return render(request, 'quizApp/quizList.html', {
        'quizzes': quizzes,
        'words': words
    })


@login_required
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
def save_quiz_attempt(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            total_score = data.get("total_score", 0)
            max_score = data.get("max_score", 0)
            total_questions = data.get("total_questions", 0)
            selected_word = data.get("selected_word", "")

            user = request.user if request.user.is_authenticated else None
            if not user:
                return JsonResponse({"error": "User not authenticated"}, status=401)
            
            print(data)
            # Fetch the Word object
            if selected_word.upper() == "ALL" or selected_word == "":
                word = None
            else:
                word = Word.objects.filter(word=selected_word).first()
                if not word:
                    return JsonResponse({"error": "Selected word not found"}, status=400)

            # Save the quiz attempt with the corresponding Word object
            QuizAttempt.objects.create(user=user, word=word, score=total_score, maxScore = max_score)

            return JsonResponse({"message": "Quiz attempt saved successfully", "score": total_score})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)


def filter_quizzes(request):
    selected_word = request.GET.get('word', 'All')

    # Filter quizzes based on selected word
    if selected_word != 'All':
        quizzes = MCQ.objects.filter(word__word=selected_word)
    else:
        quizzes = MCQ.objects.all()

    # Render the filtered quizzes as HTML
    filtered_quizzes_html = render_to_string('quizApp/quizCard.html', {'quizzes': quizzes})
    # Return the HTML as part of the AJAX response
    return JsonResponse({'filtered_quizzes_html': filtered_quizzes_html})

