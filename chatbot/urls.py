# chatbot/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('chat/', views.chat, name='chat'),
    path('process_pdf/', views.process_pdf, name='process_pdf'),
]
