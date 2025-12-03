from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our ViewSet with it
router = DefaultRouter()
router.register(r'books_all', views.BookViewSet, basename='book_all')

app_name = 'api'

urlpatterns = [
    # Route for the BookList view (ListAPIView) - original implementation
    path('books/', views.BookList.as_view(), name='book-list'),
    
    # Include the router URLs for BookViewSet (all CRUD operations)
    path('', include(router.urls)),  # This includes all routes registered with the router
]
