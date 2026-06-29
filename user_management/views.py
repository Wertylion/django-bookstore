from django.shortcuts import render

# Create your views here.

class UserFeedbackForm:
    pass


def user_feedback(request):
    if request.method == 'POST':
        feedback_form = UserFeedbackForm(request.POST)
        if feedback_form.is_valid():
            feedback_form.save()
            return render(request, 'user_feedback.html', context={'feedback_form': UserFeedbackForm()})
    else:
        feedback_form = UserFeedbackForm()
    return render(request, 'user_feedback.html', context={'feedback_form' : UserFeedbackForm() })
