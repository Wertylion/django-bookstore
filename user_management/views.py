# user_management/views.py

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView

from .forms import CustomUserCreationForm, UserFeedbackForm


class UserFeedback(LoginRequiredMixin, FormView):
    form_class = UserFeedbackForm
    template_name = 'user_feedback.html'

    def form_valid(self, form):
        return HttpResponse('Дякуємо за відгук!')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['feedback_form'] = context['form']
        return context


class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'register.html'
    success_url = reverse_lazy('login')  # редірект на сторінку логіну після реєстрації
