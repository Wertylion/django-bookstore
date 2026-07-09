
from django.urls import path
from .views import UserFeedback

urlpatterns = [
    path('feedback/', UserFeedback.as_view(), name='user_feedback'),
]
