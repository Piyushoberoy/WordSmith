from django.shortcuts import render
from django.http import JsonResponse
from .models import MCQ
from dictApp.models import Word
from userApp.models import CustomUser
from .utils import generate_mcq
import random

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


def quiz_list(request):
    """
    Retrieves all stored MCQs and renders them in a template.
    """
    quizzes = MCQ.objects.all()
    return render(request, 'quizApp/quizList.html', {'quizzes': quizzes})
