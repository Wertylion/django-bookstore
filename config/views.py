from django.shortcuts import render


def error_404(request, exception):
    return render(request, 'error_404.html', status=404)


def error_401_403(request, exception):
    return render(request, 'error_no_access.html', status=403)


def error_500(request):
    return render(request, 'error_500.html', status=500)
