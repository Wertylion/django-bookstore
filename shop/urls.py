from django.urls import path

from .views import (
    AuthorOrTitleBooksView,
    BookCreateView,
    BookDeleteView,
    BookDetailView,
    BookListView,
    BookSearchView,
    BookUpdateView,
    CategoryDetailView,
    CategoryStatsView,
    CreateFeedbackView,
    FeedbackUpdateView,
    LowStockBooksView,
    MainPageView,
    async_available_books,
    async_book_detail,
    async_catalog_summary,
)

app_name = 'shop'

urlpatterns = [
    path('', MainPageView.as_view(), name='home'),
    path('book/', MainPageView.as_view(), name='book_home'),
    path('books/', BookListView.as_view(), name='book_list'),
    path('books/search/', BookSearchView.as_view(), name='book_search'),
    path('books/new/', BookCreateView.as_view(), name='book_create'),
    path('books/<int:pk>/', BookDetailView.as_view(), name='book_detail'),
    path('books/<int:pk>/edit/', BookUpdateView.as_view(), name='book_update'),
    path('books/<int:pk>/delete/', BookDeleteView.as_view(), name='book_delete'),
    path('books/low-stock/', LowStockBooksView.as_view(), name='low_stock'),
    path('books/by-author-or-title/', AuthorOrTitleBooksView.as_view(), name='author_or_title_books'),
    path('categories/stats/', CategoryStatsView.as_view(), name='category_stats'),
    path('category/<slug:slug>/', CategoryDetailView.as_view(), name='category_detail'),
    path('book/<int:pk>/feedback/', CreateFeedbackView.as_view(), name='new_feedback'),
    path('book/<int:pk>/feedback/edit/', FeedbackUpdateView.as_view(), name='edit_feedback'),
    path('async/summary/', async_catalog_summary, name='async_catalog_summary'),
    path('async/books/', async_available_books, name='async_available_books'),
    path('async/books/<int:pk>/', async_book_detail, name='async_book_detail'),
]
