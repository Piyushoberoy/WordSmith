from .models import Word, Idiom
from django.contrib import messages
from .forms import WordForm, IdiomForm
from django.shortcuts import render, redirect
from quizApp.views import create_mcq, create_idiom_mcq
from django.contrib.auth.decorators import login_required
from .utils import generate_word_details, generate_idiom_details

@login_required
def add_word(request):
    if request.method == 'POST':
        print("[INFO] Received POST request to add a new word.")
        form = WordForm(request.POST)
        
        if form.is_valid():
            print("[INFO] Form is valid. Processing the word...")
            word = form.save(commit=False)  # Don't save yet

            # Generate missing details only if not provided
            print(f"[DEBUG] Generating details for word: {word.word}")
            generated_meaning, generated_synonyms, generated_antonyms, generated_example = generate_word_details(word.word)

            # Print generated details
            print("[DEBUG] Generated details:")
            print(f" - Meaning: {generated_meaning}")
            print(f" - Synonyms: {generated_synonyms}")
            print(f" - Antonyms: {generated_antonyms}")
            print(f" - Examples: {generated_example}")
            
            if not word.meaning:
                word.meaning = generated_meaning
                print(f"[DEBUG] Auto-filled missing meaning.")
            if not word.synonyms:
                word.synonyms = ", ".join(generated_synonyms)
                print(f"[DEBUG] Auto-filled missing synonyms.")
            if not word.antonyms:
                word.antonyms = ", ".join(generated_antonyms)
                print(f"[DEBUG] Auto-filled missing antonyms.")
            if not word.example:
                word.example = generated_example
                print(f"[DEBUG] Auto-filled missing example")

            print("[INFO] Completed filling missing details.")
            
            # Assign the logged-in user as the creator
            word.created_by = request.user
            print(f"[INFO] Word assigned to user: {request.user}")

            if Word.objects.filter(word=word.word).exists():
                print("[WARNING] Word already exists in the dictionary!")
                messages.error(request, "This word already exists in the dictionary!")
            else:
                word.save()
                print(f"[INFO] Word {word.word} saved successfully. Attempting to create MCQs...")

                # Attempt to create MCQs
                print("[INFO] Attempting to create MCQs...")
                mcq_response = create_mcq(request, word.word)
                print(f"[DEBUG] MCQ Response: {mcq_response}")

                # Check if MCQ creation was successful
                if mcq_response.status_code == 200 and "error" not in mcq_response:
                    messages.success(request, f"Word '{word.word}' added successfully!")
                    print("[INFO] Word added successfully along with MCQs.")
                    return redirect('add_word')
                else:
                    print("[ERROR] Failed to create MCQs. Deleting the saved word...")
                    Word.objects.filter(word=word.word).delete()  # Delete the saved word if MCQ creation fails
                    error_message = mcq_response.get("error", "Failed to create MCQs.")
                    print(f"[ERROR] MCQ creation failed: {error_message}")
                    messages.error(request, f"Error adding word: {error_message}")

        else:
            error = form.errors.get('word', [])[0]
            print(f"[WARNING] {error}")
            messages.error(request, error)

    else:
        print("[INFO] Received GET request. Rendering add word form.")
        form = WordForm()

    return render(request, 'dictApp/addWord.html', {'form': form})

@login_required
def view_dictionary(request):
    print("[INFO] Received request to view dictionary.")

    # Fetch all words from the database
    words = Word.objects.filter(created_by=request.user)
    print(f"[DEBUG] Retrieved {words.count()} words from the database.")

    # Render the template with the retrieved words
    print("[INFO] Rendering dictionary view template.")
    return render(request, 'dictApp/view_dictionary.html', {'words': words})

@login_required
def add_idiom(request):
    if request.method == 'POST':
        print("[INFO] Received POST request to add an idiom.")
        form = IdiomForm(request.POST)

        if form.is_valid():
            print("[INFO] Form is valid. Processing idiom data...")
            idiom = form.save(commit=False)  # Don't save yet
            print("[DEBUG] Idiom object created but not saved yet.")

            # Generate missing details only if not provided
            print(f"[DEBUG] Generating details for idiom: {idiom.phrase}")
            generated_meaning, generated_example, generated_insights, generated_category, generated_related_idioms, generated_origin, generated_difficulty_level, generated_tags = generate_idiom_details(idiom.phrase)

            # Print generated details
            print("[DEBUG] Generated details:")
            print(f" - Meaning: {generated_meaning}")
            print(f" - Example: {generated_example}")
            print(f" - Insights: {generated_insights}")
            print(f" - Category: {generated_category}")
            print(f" - Related Idioms: {generated_related_idioms}")
            print(f" - Origin: {generated_origin}")
            print(f" - Difficulty Level: {generated_difficulty_level}")
            print(f" - Tags: {generated_tags}")

            # Fill in missing details only if not provided
            if not idiom.meaning:
                idiom.meaning = generated_meaning
                print("[DEBUG] Auto-filled missing meaning.")
            if not idiom.example:
                idiom.example = generated_example
                print("[DEBUG] Auto-filled missing example.")
            if not idiom.insights:
                idiom.insights = generated_insights
                print("[DEBUG] Auto-filled missing insights.")
            if not idiom.category:
                idiom.category = generated_category
                print("[DEBUG] Auto-filled missing category.")
            if not idiom.related_idioms or idiom.related_idioms.strip() == "":
                idiom.related_idioms = ", ".join(generated_related_idioms) if generated_related_idioms else ""
                print("[DEBUG] Auto-filled missing related idioms.")
            if not idiom.origin:
                idiom.origin = generated_origin
                print("[DEBUG] Auto-filled missing origin.")
            if not idiom.difficulty_level:
                idiom.difficulty_level = generated_difficulty_level
                print("[DEBUG] Auto-filled missing difficulty level.")
            if not idiom.tags or idiom.tags.strip() == "":
                idiom.tags = ", ".join(generated_tags) if generated_tags else ""
                print("[DEBUG] Auto-filled missing tags.")

            print("[INFO] Completed filling missing details.")

            # Assign the logged-in user as the creator
            idiom.created_by = request.user
            print(f"[INFO] Idiom assigned to user: {request.user}")

            # Check if the idiom already exists
            if Idiom.objects.filter(phrase=idiom.phrase).exists():
                print("[WARNING] Idiom already exists in the dictionary.")
                messages.error(request, "This idiom already exists in the dictionary!")
            else:
                idiom.save()
                print(f"[INFO] Idiom '{idiom.phrase}' saved successfully.")

                # Attempt to create MCQs
                print("[INFO] Attempting to create MCQs...")
                mcq_response = create_idiom_mcq(request, idiom.phrase)
                print(f"[DEBUG] MCQ Response: {mcq_response}")

                # Check if MCQ creation was successful
                if mcq_response.status_code == 200 and "error" not in mcq_response:
                    messages.success(request, f"Idiom '{idiom.phrase}' added successfully!")
                    print(f"[INFO] MCQs created successfully for idiom: {idiom.phrase}")
                    return redirect('add_idiom')
                else:
                    print("[ERROR] Failed to create MCQs. Deleting the saved idiom...")
                    Idiom.objects.filter(phrase=idiom.phrase).delete()  # Delete the saved idiom if MCQ creation fails
                    error_message = mcq_response.get("error", "Failed to create MCQs.")
                    print(f"[ERROR] MCQ creation failed: {error_message}")
                    messages.error(request, f"Error adding idiom: {error_message}")

        else:
            error = form.errors.get('phrase', [])[0]
            print(f"[WARNING] {error}")
            messages.error(request, error)

    else:
        print("[INFO] Received GET request. Rendering add idiom form.")
        form = IdiomForm()

    return render(request, 'dictApp/addIdioms.html', {'form': form})

@login_required
def view_Idioms(request):
    """Displays all saved idioms."""
    print("[INFO] Received request to view idioms.")

    # Fetch all idioms from the database
    idioms = Idiom.objects.filter(created_by=request.user)
    print(f"[DEBUG] Retrieved {idioms.count()} idioms from the database.")

    # Render the template with the retrieved idioms
    print("[INFO] Rendering idioms view template.")
    return render(request, 'dictApp/view_Idiom.html', {'idioms': idioms})