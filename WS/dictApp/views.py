from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Word
from .forms import WordForm
from .utils import generate_word_details

@login_required
def add_word(request):
    if request.method == 'POST':
        form = WordForm(request.POST)
        if form.is_valid():
            word = form.save(commit=False)

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
            
            print(word)
            print(word.word, "-", word.meaning,"-", word.synonyms,"-", word.antonyms,"-", word.example,"-", word.created_by,"-", word.created_at)
            # Assign the logged-in user as the creator
            word.created_by = request.user
            word.save()

            messages.success(request, f"Word '{word.word}' added successfully!")
            return redirect('add_word')
    else:
        form = WordForm()

    return render(request, 'dictApp/addWord.html', {'form': form})
