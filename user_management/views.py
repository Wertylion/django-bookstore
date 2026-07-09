# user_management/views.py

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import View

from .forms import UserFeedbackForm


def user_feedback(request):
    if request.method == 'POST':
        feedback_form = UserFeedbackForm(request.POST)
        if feedback_form.is_valid():
            return redirect('book_list')  # після успіху — редирект
    else:
        feedback_form = UserFeedbackForm()

    return render(request, 'user_feedback.html', {'feedback_form': feedback_form})


class UserFeedback(LoginRequiredMixin, View):
    def get(self, request):
        feedback_form = UserFeedbackForm()
        return render(request, 'user_feedback.html', {'feedback_form': feedback_form})

    def post(self, request):
        feedback_form = UserFeedbackForm(request.POST)
        if feedback_form.is_valid():
            return HttpResponse('Дякуємо за відгук!')
        return render(request, 'user_feedback.html', {'feedback_form': feedback_form})
