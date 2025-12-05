"""
Views for the advanced-api-project API.

This module contains various types of views demonstrating Django REST Framework's capabilities:
1. Generic Views for CRUD operations
2. Custom APIViews for specialized operations
3. ViewSets for consolidated operations
"""

# Django REST Framework imports
from rest_framework import generics, permissions, filters, status, viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
import django.db.models as models
from .models import Author, Book
from .serializers import AuthorSerializer, BookSerializer, BookDetailSerializer


# ============================================
# BOOK VIEWS (Generic Views)
# ============================================

class BookListView(generics.ListAPIView):
    """
    List all books.
    
    Generic View Features:
    - Uses ListAPIView for efficient list operations
    - Supports pagination, filtering, and ordering
    - Read-only access for all users
    
    Endpoint: GET /api/books/
    Permissions: AllowAny (read-only)
    """
    queryset = Book.objects.all().select_related('author')
    serializer_class = BookSerializer
    permission_classes = [AllowAny]  # Use imported AllowAny
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Filtering options
    filterset_fields = ['author__name', 'publication_year']
    
    # Search options
    search_fields = ['title', 'author__name']
    
    # Ordering options
    ordering_fields = ['title', 'publication_year', 'author__name']
    ordering = ['title']  # Default ordering
    
    def get_queryset(self):
        """
        Optionally override to customize queryset based on request.
        Example: Filter by year range
        """
        queryset = super().get_queryset()
        
        # Get query parameters
        min_year = self.request.query_params.get('min_year')
        max_year = self.request.query_params.get('max_year')
        
        if min_year:
            queryset = queryset.filter(publication_year__gte=min_year)
        if max_year:
            queryset = queryset.filter(publication_year__lte=max_year)
        
        return queryset


class BookDetailView(generics.RetrieveAPIView):
    """
    Retrieve a specific book by ID.
    
    Generic View Features:
    - Uses RetrieveAPIView for single object retrieval
    - Includes related author information
    - Read-only access for all users
    
    Endpoint: GET /api/books/<id>/
    Permissions: AllowAny (read-only)
    """
    queryset = Book.objects.all().select_related('author')
    serializer_class = BookDetailSerializer  # Use detailed serializer with nested author
    permission_classes = [AllowAny]  # Use imported AllowAny
    lookup_field = 'pk'  # Default, can be changed to other fields


class BookCreateView(generics.CreateAPIView):
    """
    Create a new book.
    
    Generic View Features:
    - Uses CreateAPIView for object creation
    - Handles POST requests with data validation
    - Restricted to authenticated users
    
    Endpoint: POST /api/books/create/
    Permissions: IsAuthenticated (imported)
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]  # Use imported IsAuthenticated
    
    def perform_create(self, serializer):
        """
        Override to add custom logic before saving.
        """
        serializer.save()
        print(f"Book created: {serializer.instance.title}")


class BookUpdateView(generics.UpdateAPIView):
    """
    Update an existing book.
    
    Generic View Features:
    - Uses UpdateAPIView for full object updates
    - Also handles partial updates (PATCH)
    - Restricted to authenticated users
    
    Endpoint: PUT /api/books/update/
    Endpoint: PATCH /api/books/update/
    Also supports: PUT/PATCH /api/books/update/<pk>/
    Permissions: IsAuthenticated (imported)
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]  # Use imported IsAuthenticated
    lookup_field = 'pk'
    
    def get_object(self):
        """
        Get book object. Supports both patterns.
        """
        # If pk is in URL kwargs, use it
        if 'pk' in self.kwargs:
            return super().get_object()
        
        # Otherwise, try to get pk from request data
        pk = self.request.data.get('id') or self.request.data.get('pk')
        if pk:
            return generics.get_object_or_404(Book, pk=pk)
        
        from rest_framework.exceptions import ValidationError
        raise ValidationError(
            {'detail': 'Book ID is required in URL or request data.'}
        )
    
    def perform_update(self, serializer):
        """Custom logic before updating."""
        serializer.save()


class BookDeleteView(generics.DestroyAPIView):
    """
    Delete a book.
    
    Generic View Features:
    - Uses DestroyAPIView for object deletion
    - Returns 204 No Content on success
    - Restricted to admin users only
    
    Endpoint: DELETE /api/books/delete/
    Also supports: DELETE /api/books/delete/<pk>/
    Permissions: IsAdminUser (imported)
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminUser]  # Use imported IsAdminUser
    lookup_field = 'pk'
    
    def get_object(self):
        """
        Get book object. Supports both patterns.
        """
        # If pk is in URL kwargs, use it
        if 'pk' in self.kwargs:
            return super().get_object()
        
        # Otherwise, try to get pk from request data
        pk = self.request.data.get('id') or self.request.data.get('pk')
        if pk:
            return generics.get_object_or_404(Book, pk=pk)
        
        from rest_framework.exceptions import ValidationError
        raise ValidationError(
            {'detail': 'Book ID is required in URL or request data.'}
        )
    
    def perform_destroy(self, instance):
        """Custom logic before deletion."""
        instance.delete()


# ============================================
# AUTHOR VIEWS (Generic Views)
# ============================================

class AuthorListView(generics.ListAPIView):
    """List all authors."""
    queryset = Author.objects.all().prefetch_related('books')
    serializer_class = AuthorSerializer
    permission_classes = [AllowAny]  # Use imported AllowAny
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']
    ordering = ['name']


class AuthorDetailView(generics.RetrieveAPIView):
    """Retrieve a specific author by ID."""
    queryset = Author.objects.all().prefetch_related('books')
    serializer_class = AuthorSerializer
    permission_classes = [AllowAny]  # Use imported AllowAny
    lookup_field = 'pk'


class AuthorCreateView(generics.CreateAPIView):
    """Create a new author."""
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticated]  # Use imported IsAuthenticated


class AuthorUpdateView(generics.UpdateAPIView):
    """Update an existing author."""
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticated]  # Use imported IsAuthenticated
    lookup_field = 'pk'


class AuthorDeleteView(generics.DestroyAPIView):
    """Delete an author."""
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAdminUser]  # Use imported IsAdminUser
    lookup_field = 'pk'


# ============================================
# CUSTOM VIEWS (Example of non-generic views)
# ============================================

class BookStatsView(APIView):
    """
    Custom view for book statistics.
    
    This demonstrates a non-generic APIView for custom functionality.
    
    Endpoint: GET /api/books/stats/
    """
    permission_classes = [AllowAny]  # Use imported AllowAny
    
    def get(self, request, format=None):
        """
        Return book statistics.
        """
        total_books = Book.objects.count()
        total_authors = Author.objects.count()
        
        # Books by year
        years = Book.objects.values('publication_year').annotate(
            count=models.Count('id')
        ).order_by('-publication_year')[:10]
        
        # Most prolific authors
        prolific_authors = Author.objects.annotate(
            book_count=models.Count('books')
        ).order_by('-book_count')[:5]
        
        stats = {
            'total_books': total_books,
            'total_authors': total_authors,
            'books_by_year': list(years),
            'prolific_authors': [
                {
                    'name': author.name,
                    'book_count': author.book_count
                }
                for author in prolific_authors
            ]
        }
        
        return Response(stats, status=status.HTTP_200_OK)


class BookBulkCreateView(APIView):
    """
    Custom view for bulk book creation.
    
    Demonstrates handling complex operations not covered by generic views.
    
    Endpoint: POST /api/books/bulk-create/
    """
    permission_classes = [IsAdminUser]  # Use imported IsAdminUser
    
    def post(self, request, format=None):
        """
        Create multiple books at once.
        """
        books_data = request.data
        
        if not isinstance(books_data, list):
            return Response(
                {'error': 'Expected a list of books'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created_books = []
        errors = []
        
        for book_data in books_data:
            serializer = BookSerializer(data=book_data)
            if serializer.is_valid():
                serializer.save()
                created_books.append(serializer.data)
            else:
                errors.append({
                    'data': book_data,
                    'errors': serializer.errors
                })
        
        response_data = {
            'created': len(created_books),
            'failed': len(errors),
            'books': created_books,
            'errors': errors if errors else None
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)


# ============================================
# VIEWSET (Alternative approach)
# ============================================

class BookViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Book model - alternative to separate generic views.
    
    Provides all CRUD operations in a single class.
    Automatically generates appropriate URLs.
    """
    queryset = Book.objects.all().select_related('author')
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # Use imported IsAuthenticatedOrReadOnly
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['author', 'publication_year']
    search_fields = ['title', 'author__name']
    
    def get_serializer_class(self):
        """
        Use different serializers for different actions.
        """
        if self.action == 'retrieve':
            return BookDetailSerializer
        return BookSerializer
    
    def get_permissions(self):
        """
        Customize permissions per action.
        """
        if self.action == 'destroy':
            return [IsAdminUser()]  # Use imported IsAdminUser
        return super().get_permissions()
    
    @action(detail=True, methods=['get'])
    def similar(self, request, pk=None):
        """
        Custom action: Get similar books (by same author).
        
        Endpoint: GET /api/books/<id>/similar/
        """
        book = self.get_object()
        similar_books = Book.objects.filter(
            author=book.author
        ).exclude(pk=book.pk)
        
        page = self.paginate_queryset(similar_books)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(similar_books, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """
        Custom action: Get recently published books.
        
        Endpoint: GET /api/books/recent/
        """
        recent_books = Book.objects.order_by('-publication_year')[:10]
        serializer = self.get_serializer(recent_books, many=True)
        return Response(serializer.data)
