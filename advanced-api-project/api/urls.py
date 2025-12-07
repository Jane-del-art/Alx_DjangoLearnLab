from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router for ViewSet
router = DefaultRouter()
router.register(r'books-viewset', views.BookViewSet, basename='book-viewset')

app_name = 'api'

urlpatterns = [
    # ============================================
    # BOOK URLS
    # ============================================
    
    # List all books with filtering, searching, ordering
    path('books/', views.BookListView.as_view(), name='book-list'),
    
    # Retrieve specific book
    path('books/<int:pk>/', views.BookDetailView.as_view(), name='book-detail'),
    
    # Create new book
    path('books/create/', views.BookCreateView.as_view(), name='book-create'),
    
    # Update existing book
    path('books/update/', views.BookUpdateView.as_view(), name='book-update'),
    path('books/update/<int:pk>/', views.BookUpdateView.as_view(), name='book-update-detail'),
    
    # Delete book
    path('books/delete/', views.BookDeleteView.as_view(), name='book-delete'),
    path('books/delete/<int:pk>/', views.BookDeleteView.as_view(), name='book-delete-detail'),
    
    # ============================================
    # AUTHOR URLS
    # ============================================
    
    # List all authors with filtering
    path('authors/', views.AuthorListView.as_view(), name='author-list'),
    
    # ============================================
    # DEMO & DOCUMENTATION URLS
    # ============================================
    
    # Filtering demonstration endpoint
    path('filtering-demo/', views.FilteringDemoView.as_view(), name='filtering-demo'),
    
    # ============================================
    # VIEWSET URLS
    # ============================================
    
    # Include ViewSet URLs
    path('', include(router.urls)),
]
