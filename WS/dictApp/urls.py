from django.urls import path, include
from .views import add_word


urlpatterns = [
    path('', add_word, name='add_word'),
]