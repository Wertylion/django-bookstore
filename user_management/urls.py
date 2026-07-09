
from django.urls import path
from .views import UserFeedback, RegisterView

urlpatterns = [
    path('feedback/', UserFeedback.as_view(), name='user_feedback'),
    path('register/', RegisterView.as_view(), name='register'),
]
