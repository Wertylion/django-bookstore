
from django.urls import path
from .views import UserFeedback, RegisterView

app_name = 'user_management'

urlpatterns = [
    path('feedback/', UserFeedback.as_view(), name='user_feedback'),
    path('register/', RegisterView.as_view(), name='register'),
]
