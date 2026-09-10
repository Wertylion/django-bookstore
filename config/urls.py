
from django.contrib import admin
from django.conf import settings
from django.urls import path, include

from config.views import error_401_403, error_404, error_500
from user_management.views import RegisterView

handler404 = error_404
handler500 = error_500
handler403 = error_401_403

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('', include(('shop.urls', 'shop'), namespace='shop')),
    path('', include('django.contrib.auth.urls')),
    path('register/', RegisterView.as_view(), name='register'),
    path('order/', include(('order.urls', 'order'), namespace='order')),
    path('user/', include(('user_management.urls', 'user_management'), namespace='user_management')),
]

if settings.DEBUG and 'debug_toolbar' in settings.INSTALLED_APPS:
    urlpatterns.append(path('__debug__/', include('debug_toolbar.urls')))
