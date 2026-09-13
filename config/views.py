from django.shortcuts import render
from django.http import JsonResponse


def health_check(request):
    """Return a lightweight response for load balancers and container checks."""

    return JsonResponse({"status": "ok"})


def error_404(request, exception):
    """Render the custom 404 page."""

    return render(request, "error_404.html", status=404)


def error_401_403(request, exception):
    """Render the custom 403 page."""

    return render(request, "error_no_access.html", status=403)


def error_500(request):
    """Render the custom 500 page."""

    return render(request, "error_500.html", status=500)
