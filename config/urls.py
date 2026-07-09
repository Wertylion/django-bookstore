
from django.contrib import admin
from django.urls import path, include

from shop import views
from shop.views import main_page
from config.views import error_401_403, error_404, error_500

handler404 = error_404
handler500 = error_500
handler403 = error_401_403

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', main_page),
    path('book/', main_page),
    path('books/', views.book_list, name='book_list'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('book/<int:pk>/feedback/', views.CreateFeedbackView.as_view(), name='new_feedback'),
    path('book/<int:pk>/feedback/edit/', views.FeedbackUpdateView.as_view(), name='edit_feedback'),
    path('order/', include('order.urls')),               # /order/new/
    path('user/', include('user_management.urls')),      # /user/feedback/
]
