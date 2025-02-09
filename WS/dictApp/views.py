from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Word
from .forms import WordForm
from .utils import generate_word_details
from quizApp.views import create_mcq

@login_required
def add_word(request):
    if request.method == 'POST':
        form = WordForm(request.POST)
        if form.is_valid():
            word = form.save(commit=False)  # Don't save yet

            # Generate missing details only if not provided by the user
            generated_meaning, generated_synonyms, generated_antonyms, generated_example = generate_word_details(word.word)

            if not word.meaning:
                word.meaning = generated_meaning
            if not word.synonyms:
                word.synonyms = ", ".join(generated_synonyms)
            if not word.antonyms:
                word.antonyms = ", ".join(generated_antonyms)
            if not word.example:
                word.example = generated_example
            
            # Assign the logged-in user as the creator
            word.created_by = request.user
            word.save()
            print("Attempting to create MCQs...")
            mcq_response = create_mcq(request, word.word)
            print(mcq_response)
            # Check if MCQ creation was successful
            if mcq_response.status_code == 200 and "error" not in mcq_response:
                messages.success(request, f"Word '{word.word}' added successfully!")
                return redirect('add_word')
            else:
                print("Failed to create MCQs. Deleting the saved word...")
                Word.objects.filter(word=word.word).delete()  # Delete the saved word if MCQ creation fails
                error_message = mcq_response.get("error", "Failed to create MCQs.")
                messages.error(request, f"Error adding word: {error_message}")
        else:
            messages.error(request, "Invalid form submission. Please check your input.")

    else:
        form = WordForm()

    return render(request, 'dictApp/addWord.html', {'form': form})
