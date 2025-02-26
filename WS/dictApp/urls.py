from django.urls import path, include
from .views import *


urlpatterns = [
    path('', view_dictionary, name='view_dictionary'),
    path('addWord/', add_word, name='add_word'),
    path('viewIdioms/', view_Idioms, name='view_Idioms'),
    path('addIdioms/', add_idiom, name='add_idiom'),
]