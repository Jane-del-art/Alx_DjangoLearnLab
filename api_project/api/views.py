from rest_framework import generics
from .models import Book
from .serializers import BookSerializer

class BookList(generics.ListAPIView):
    """
    API endpoint that allows books to be viewed.
    
    This view returns a list of all books in the database.
    Uses ListAPIView which provides GET method handler.
    """
    queryset = Book.objects.all()  # Get all books from database
    serializer_class = BookSerializer  # Use BookSerializer to convert to JSON
    
