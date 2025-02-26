from django import forms
from .models import Word, Idiom

class WordForm(forms.ModelForm):
    class Meta:
        model = Word
        fields = '__all__'
        
    def clean_word(self):
        word = self.cleaned_data.get('word')
        if Word.objects.filter(word__iexact=word).exists():
            raise forms.ValidationError(f"'{word}' already exists in the your dictionary.")
        
        return word
    
class IdiomForm(forms.ModelForm):
    difficulty_level = forms.ChoiceField(
        choices=[('Beginner', 'Beginner'), ('Intermediate', 'Intermediate'), ('Advanced', 'Advanced')],
        initial='Beginner', # Set default value
        required=False
    )
    class Meta:
        model = Idiom
        fields = '__all__'
    
    def clean_phrase(self):
        phrase = self.cleaned_data.get('phrase')
        if Idiom.objects.filter(phrase__iexact=phrase).exists():
            raise forms.ValidationError(f"'{phrase}' already exists in your dictionary.")
        
        return phrase