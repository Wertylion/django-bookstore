"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from shop.views import main_page
# from order.views import new_order
# from user_manegment.views import user_feedback, user_register

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', main_page),
    path('book/', main_page),
#     path('book/<int:book_id>', specidic_book),
#     path('user_feedback/', user_feedback),
#     path('nwe_order/', new_order),
#     path('register/', user_register),
]
