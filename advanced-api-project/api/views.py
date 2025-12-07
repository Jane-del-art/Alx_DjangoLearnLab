"""
Views for the advanced-api-project API with filtering, searching, and ordering.
"""

# Django REST Framework imports
from rest_framework import generics, permissions, filters, status, viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action

from django_filters import rest_framework

# Django imports
import django.db.models as models

# Local imports
from .models import Author, Book
from .serializers import AuthorSerializer, BookSerializer, BookDetailSerializer
from .filters import BookFilter, AuthorFilter, CustomSearchFilter, CustomOrderingFilter


# ============================================
# ENHANCED BOOK VIEWS WITH FILTERING, SEARCHING, ORDERING
# ============================================

class BookListView(generics.ListAPIView):
    """
    List all books with advanced filtering, searching, and ordering capabilities.
    
    Features:
    - Filtering: Filter by title, author, publication year, etc.
    - Searching: Full-text search on title and author fields
    - Ordering: Sort by any field in ascending or descending order
    - Pagination: Results are paginated (20 per page)
    
    Query Parameters:
    - Filtering:
        ?title=1984                      # Books with '1984' in title
        ?author_name=Orwell              # Books by authors with 'Orwell' in name
        ?publication_year=1949           # Books published in 1949
        ?min_year=1900&max_year=2000     # Books between 1900 and 2000
        ?recent=true                     # Books published in last 10 years
    
    - Searching:
        ?search=Orwell                   # Search in title and author fields
        ?q=1984                          # Alternative search parameter
    
    - Ordering:
        ?ordering=title                  # Sort by title ascending
        ?ordering=-publication_year      # Sort by publication year descending
        ?sort=author__name               # Using custom ordering parameter
    
    - Pagination:
        ?page=2                          # Get page 2 of results
        ?page_size=50                    # Show 50 items per page
    
    Endpoint: GET /api/books/
    Permissions: AllowAny (read-only)
    """
    queryset = Book.objects.all().select_related('author')
    serializer_class = BookSerializer
    permission_classes = [AllowAny]
    
    # Configure filter backends
    filter_backends = [
        rest_framework.DjangoFilterBackend,      # For field-based filtering
        filters.SearchFilter,                    # For search functionality
        filters.OrderingFilter,                  # For ordering functionality
    ]
    
    # DjangoFilterBackend configuration
    filterset_class = BookFilter  # Use our custom BookFilter class
    
    # SearchFilter configuration
    search_fields = ['title', 'author__name', '^title']  # ^ for starts-with search
    
    # OrderingFilter configuration
    ordering_fields = ['title', 'publication_year', 'author__name']
    ordering = ['title']  # Default ordering
    
    # Pagination
    paginate_by = 20
    paginate_by_param = 'page_size'
    max_paginate_by = 100
    
    def get_queryset(self):
        """
        Override to add custom queryset optimizations and additional filtering.
        
        This method demonstrates:
        1. Basic queryset optimization with select_related
        2. Custom filtering logic beyond what filterset provides
        3. Dynamic queryset modifications based on request
        """
        queryset = super().get_queryset()
        
        # Example: Custom filter for decade
        decade = self.request.query_params.get('decade')
        if decade and decade.isdigit():
            decade = int(decade)
            queryset = queryset.filter(
                publication_year__gte=decade,
                publication_year__lt=decade + 10
            )
        
        # Example: Custom filter for century
        century = self.request.query_params.get('century')
        if century and century.isdigit():
            century = int(century)
            start_year = (century - 1) * 100 + 1
            end_year = century * 100
            queryset = queryset.filter(
                publication_year__gte=start_year,
                publication_year__lte=end_year
            )
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """
        Override list method to add metadata about filtering options.
        
        This provides API consumers with information about available
        filtering, searching, and ordering options.
        """
        response = super().list(request, *args, **kwargs)
        
        # Add metadata about available filters
        response.data['metadata'] = {
            'total_count': response.data.get('count', len(response.data)),
            'filtering_options': {
                'title': 'Filter by book title (case-insensitive partial match)',
                'author_name': 'Filter by author name (case-insensitive partial match)',
                'publication_year': 'Filter by exact publication year',
                'min_year': 'Filter by minimum publication year',
                'max_year': 'Filter by maximum publication year',
                'publication_year_range': 'Filter by publication year range (e.g., 1900-2000)',
                'recent': 'Filter for recent books (published in last 10 years)',
                'author': 'Filter by one or more authors (provide author IDs)',
                'decade': 'Filter by decade (e.g., 1980 for 1980-1989)',
                'century': 'Filter by century (e.g., 20 for 1901-2000)',
            },
            'searching_options': {
                'search': 'Search in title and author fields',
                'q': 'Alternative search parameter',
            },
            'ordering_options': {
                'title': 'Sort by book title (ascending)',
                '-title': 'Sort by book title (descending)',
                'publication_year': 'Sort by publication year (ascending)',
                '-publication_year': 'Sort by publication year (descending)',
                'author__name': 'Sort by author name (ascending)',
                '-author__name': 'Sort by author name (descending)',
                'ordering': 'Use ordering parameter (default)',
                'sort': 'Alternative ordering parameter',
            },
            'pagination_options': {
                'page': 'Page number (default: 1)',
                'page_size': 'Items per page (default: 20, max: 100)',
            }
        }
        
        return response


class BookDetailView(generics.RetrieveAPIView):
    """
    Retrieve a specific book by ID.
    
    Enhanced with related data and filtering context.
    
    Endpoint: GET /api/books/<id>/
    Permissions: AllowAny (read-only)
    """
    queryset = Book.objects.all().select_related('author')
    serializer_class = BookDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'pk'


class BookCreateView(generics.CreateAPIView):
    """
    Create a new book.
    
    Endpoint: POST /api/books/create/
    Permissions: IsAuthenticated
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save()


class BookUpdateView(generics.UpdateAPIView):
    """
    Update an existing book.
    
    Endpoint: PUT /api/books/update/
    Endpoint: PATCH /api/books/update/
    Also supports: PUT/PATCH /api/books/update/<pk>/
    Permissions: IsAuthenticated
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'


class BookDeleteView(generics.DestroyAPIView):
    """
    Delete a book.
    
    Endpoint: DELETE /api/books/delete/
    Also supports: DELETE /api/books/delete/<pk>/
    Permissions: IsAdminUser
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'pk'


# ============================================
# ENHANCED AUTHOR VIEWS
# ============================================

class AuthorListView(generics.ListAPIView):
    """
    List all authors with filtering and searching capabilities.
    
    Query Parameters:
    - Filtering:
        ?name=Austen                     # Authors with 'Austen' in name
        ?has_books=true                  # Authors who have books
    
    - Searching:
        ?search=Orwell                   # Search in author names
    
    - Ordering:
        ?ordering=name                   # Sort by name
        ?ordering=-name                  # Sort by name descending
    
    Endpoint: GET /api/authors/
    Permissions: AllowAny
    """
    queryset = Author.objects.all().prefetch_related('books')
    serializer_class = AuthorSerializer
    permission_classes = [AllowAny]
    filter_backends = [rest_framework.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = AuthorFilter
    search_fields = ['name']
    ordering_fields = ['name', 'book_count']
    ordering = ['name']


# ============================================
# API TEST VIEW (For demonstrating features)
# ============================================

class FilteringDemoView(APIView):
    """
    Demonstration view showing all filtering, searching, and ordering features.
    
    This view provides examples and documentation for API consumers.
    
    Endpoint: GET /api/filtering-demo/
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """
        Return documentation and examples for filtering features.
        """
        examples = {
            'title': 'Filtering, Searching, and Ordering API Demo',
            'description': 'This endpoint demonstrates all available filtering, searching, and ordering features.',
            
            'filtering_examples': [
                {
                    'description': 'Filter by title containing text',
                    'url': '/api/books/?title=1984',
                    'method': 'GET'
                },
                {
                    'description': 'Filter by author name',
                    'url': '/api/books/?author_name=Orwell',
                    'method': 'GET'
                },
                {
                    'description': 'Filter by exact publication year',
                    'url': '/api/books/?publication_year=1949',
                    'method': 'GET'
                },
                {
                    'description': 'Filter by year range',
                    'url': '/api/books/?min_year=1900&max_year=2000',
                    'method': 'GET'
                },
                {
                    'description': 'Filter recent books (last 10 years)',
                    'url': '/api/books/?recent=true',
                    'method': 'GET'
                },
                {
                    'description': 'Filter by decade',
                    'url': '/api/books/?decade=1980',
                    'method': 'GET'
                },
            ],
            
            'searching_examples': [
                {
                    'description': 'Search in title and author fields',
                    'url': '/api/books/?search=Orwell',
                    'method': 'GET'
                },
                {
                    'description': 'Alternative search parameter',
                    'url': '/api/books/?q=1984',
                    'method': 'GET'
                },
            ],
            
            'ordering_examples': [
                {
                    'description': 'Order by title ascending',
                    'url': '/api/books/?ordering=title',
                    'method': 'GET'
                },
                {
                    'description': 'Order by publication year descending',
                    'url': '/api/books/?ordering=-publication_year',
                    'method': 'GET'
                },
                {
                    'description': 'Order by author name',
                    'url': '/api/books/?ordering=author__name',
                    'method': 'GET'
                },
                {
                    'description': 'Custom ordering parameter',
                    'url': '/api/books/?sort=-title',
                    'method': 'GET'
                },
            ],
            
            'pagination_examples': [
                {
                    'description': 'Get specific page',
                    'url': '/api/books/?page=2',
                    'method': 'GET'
                },
                {
                    'description': 'Change page size',
                    'url': '/api/books/?page_size=50',
                    'method': 'GET'
                },
            ],
            
            'combined_examples': [
                {
                    'description': 'Combined filtering, searching, and ordering',
                    'url': '/api/books/?author_name=Orwell&search=1984&ordering=-publication_year&page=1&page_size=10',
                    'method': 'GET',
                    'explanation': 'This combines multiple features: filters by author, searches for text, orders by year, and paginates results'
                },
            ],
            
            'available_filters': list(BookFilter.base_filters.keys()),
            'available_search_fields': ['title', 'author__name'],
            'available_ordering_fields': ['title', 'publication_year', 'author__name'],
            
            'tips': [
                'Use exact matches for IDs and specific years',
                'Use icontains for partial text matching (case-insensitive)',
                'Combine multiple filters for precise results',
                'Use range filters (min_year/max_year) for date ranges',
                'Check the metadata in list responses for available options',
            ]
        }
        
        return Response(examples)


# ============================================
# BOOK VIEWSET WITH ALL FEATURES
# ============================================

class BookViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Book model with comprehensive filtering, searching, and ordering.
    
    This ViewSet demonstrates an alternative approach using ModelViewSet
    with all filtering features integrated.
    """
    queryset = Book.objects.all().select_related('author')
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    # Filter configuration
    filter_backends = [
        rest_framework.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = BookFilter
    search_fields = ['title', 'author__name']
    ordering_fields = ['title', 'publication_year', 'author__name']
    ordering = ['title']
    
    def get_serializer_class(self):
        """Use different serializers for different actions."""
        if self.action == 'retrieve':
            return BookDetailSerializer
        return BookSerializer
    
    @action(detail=False, methods=['get'])
    def filter_options(self, request):
        """
        Custom action to list all available filtering options.
        
        Endpoint: GET /api/books/filter-options/
        """
        filter_options = {
            'filters': [
                {'name': 'title', 'type': 'string', 'description': 'Filter by book title'},
                {'name': 'author_name', 'type': 'string', 'description': 'Filter by author name'},
                {'name': 'publication_year', 'type': 'integer', 'description': 'Filter by publication year'},
                {'name': 'min_year', 'type': 'integer', 'description': 'Minimum publication year'},
                {'name': 'max_year', 'type': 'integer', 'description': 'Maximum publication year'},
                {'name': 'recent', 'type': 'boolean', 'description': 'Recent books (last 10 years)'},
            ],
            'search': {
                'fields': ['title', 'author__name'],
                'parameter': 'search',
            },
            'ordering': {
                'fields': ['title', 'publication_year', 'author__name'],
                'parameter': 'ordering',
            }
        }
        return Response(filter_options)
