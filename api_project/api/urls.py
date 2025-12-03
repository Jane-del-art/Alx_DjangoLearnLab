from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # Maps the URL 'books/' to the BookList view
    path('books/', views.BookList.as_view(), name='book-list'),
]
