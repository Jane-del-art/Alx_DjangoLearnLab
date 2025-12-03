from rest_framework import generics, viewsets
from .models import Book
from .serializers import BookSerializer

class BookList(generics.ListAPIView):
    """
    API endpoint that allows books to be viewed (original implementation).
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer

class BookViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling all CRUD operations on the Book model.
    
    Provides the following actions:
    - list: GET /books_all/ - List all books
    - create: POST /books_all/ - Create a new book
    - retrieve: GET /books_all/<id>/ - Retrieve a specific book
    - update: PUT /books_all/<id>/ - Update a specific book
    - partial_update: PATCH /books_all/<id>/ - Partially update a specific book
    - destroy: DELETE /books_all/<id>/ - Delete a specific book
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    
    def perform_create(self, serializer):
        """
        Override create to add custom logic if needed.
        """
        serializer.save()
    
    def perform_update(self, serializer):
        """
        Override update to add custom logic if needed.
        """
        serializer.save()
    
    def perform_destroy(self, instance):
        """
        Override destroy to add custom logic if needed.
        """
        instance.delete()
