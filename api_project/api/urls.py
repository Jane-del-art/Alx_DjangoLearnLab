from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from . import views

# Create a router and register our ViewSet with it
router = DefaultRouter()
router.register(r'books_all', views.BookViewSet, basename='book_all')

app_name = 'api'

urlpatterns = [
    # Authentication endpoints
    path('api-token-auth/', views.CustomObtainAuthToken.as_view(), name='api_token_auth'),
    path('api-token-auth/basic/', obtain_auth_token, name='api_token_auth_basic'),  # Basic token endpoint
    
    # Original book endpoints
    path('books/', views.BookList.as_view(), name='book-list'),
    
    # Include the router URLs for BookViewSet (all CRUD operations)
    path('', include(router.urls)),
]
