# chatbot/urls.py
from django.urls import path
from .views import ChatbotView, RequestStatusView

urlpatterns = [
    path('chat/', ChatbotView.as_view(), name='chatbot'),
    path('status/<int:request_id>/', RequestStatusView.as_view(), name='request_status'),
]