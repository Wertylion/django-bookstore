from django.contrib import admin
from django.conf import settings
from django.urls import path, include

from config.views import error_401_403, error_404, error_500, health_check
from user_management.views import RegisterView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

handler404 = error_404
handler500 = error_500
handler403 = error_401_403

urlpatterns = [
    path("health/", health_check, name="health_check"),
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="api_schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="api_schema"),
        name="api_docs",
    ),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("api/", include(("api.urls", "api"), namespace="api")),
    path("i18n/", include("django.conf.urls.i18n")),
    path("", include(("shop.urls", "shop"), namespace="shop")),
    path("", include("django.contrib.auth.urls")),
    path("register/", RegisterView.as_view(), name="register"),
    path("order/", include(("order.urls", "order"), namespace="order")),
    path(
        "user/",
        include(
            ("user_management.urls", "user_management"), namespace="user_management"
        ),
    ),
]

if settings.DEBUG and "debug_toolbar" in settings.INSTALLED_APPS:
    urlpatterns.append(path("__debug__/", include("debug_toolbar.urls")))
