"""
Custom filters for the Book model.
This module defines filtering, searching, and ordering capabilities.
"""

import django_filters
from django_filters import rest_framework as filters
from .models import Book, Author


class BookFilter(filters.FilterSet):
    """
    FilterSet for Book model with advanced filtering capabilities.
    
    Provides filtering on:
    - Exact matches (id, publication_year)
    - Partial matches (title, author name)
    - Range filtering (publication year range)
    - Choice filtering (multiple values)
    """
    
    # Exact match filters
    id = filters.NumberFilter(field_name='id', lookup_expr='exact')
    publication_year = filters.NumberFilter(field_name='publication_year', lookup_expr='exact')
    
    # Partial match filters (case-insensitive)
    title = filters.CharFilter(field_name='title', lookup_expr='icontains', 
                               help_text="Filter by book title (case-insensitive partial match)")
    
    author_name = filters.CharFilter(field_name='author__name', lookup_expr='icontains',
                                     help_text="Filter by author name (case-insensitive partial match)")
    
    # Range filters
    publication_year_range = filters.NumericRangeFilter(field_name='publication_year',
                                                       help_text="Filter by publication year range (e.g., 1900-2000)")
    
    min_year = filters.NumberFilter(field_name='publication_year', lookup_expr='gte',
                                    help_text="Filter by minimum publication year")
    
    max_year = filters.NumberFilter(field_name='publication_year', lookup_expr='lte',
                                    help_text="Filter by maximum publication year")
    
    # Choice/multiple value filters
    author = filters.ModelMultipleChoiceFilter(
        field_name='author__id',
        queryset=Author.objects.all(),
        help_text="Filter by one or more authors (provide author IDs)"
    )
    
    # Custom method filters
    recent = filters.BooleanFilter(method='filter_recent',
                                   help_text="Filter for recent books (published in last 10 years)")
    
    class Meta:
        model = Book
        fields = {
            'title': ['exact', 'icontains', 'istartswith', 'iendswith'],
            'publication_year': ['exact', 'gte', 'lte', 'gt', 'lt'],
            'author__name': ['exact', 'icontains'],
        }
    
    def filter_recent(self, queryset, name, value):
        """
        Custom filter method to get recent books.
        
        Args:
            queryset: The original queryset
            name: The filter field name
            value: Boolean value (True/False)
            
        Returns:
            Filtered queryset
        """
        import datetime
        current_year = datetime.datetime.now().year
        
        if value:
            # Return books published in the last 10 years
            return queryset.filter(publication_year__gte=current_year - 10)
        else:
            # Return books older than 10 years
            return queryset.filter(publication_year__lt=current_year - 10)
    
    @property
    def qs(self):
        """
        Override to add custom queryset optimizations.
        """
        queryset = super().qs
        # Add select_related for performance
        return queryset.select_related('author')


class AuthorFilter(filters.FilterSet):
    """
    FilterSet for Author model.
    """
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    has_books = filters.BooleanFilter(method='filter_has_books')
    
    class Meta:
        model = Author
        fields = ['name']
    
    def filter_has_books(self, queryset, name, value):
        """
        Filter authors based on whether they have books.
        """
        if value:
            return queryset.filter(books__isnull=False).distinct()
        else:
            return queryset.filter(books__isnull=True)


# Custom search backends for more control
class CustomSearchFilter(filters.SearchFilter):
    """
    Custom search filter with improved search capabilities.
    """
    search_param = 'search'  # Custom search parameter
    
    def get_search_fields(self, view, request):
        """
        Dynamically determine search fields.
        """
        # You can customize this based on view or request
        return ['title', 'author__name', '^title']  # ^ for starts-with search
    
    def filter_queryset(self, request, queryset, view):
        """
        Apply search filter with custom logic.
        """
        search_terms = self.get_search_terms(request)
        if not search_terms:
            return queryset
        
        # Custom search logic can be added here
        return super().filter_queryset(request, queryset, view)


class CustomOrderingFilter(filters.OrderingFilter):
    """
    Custom ordering filter with improved ordering capabilities.
    """
    ordering_param = 'sort'  # Custom ordering parameter
    
    def get_ordering(self, request, queryset, view):
        """
        Get ordering from request with validation.
        """
        ordering = super().get_ordering(request, queryset, view)
        
        # Validate ordering fields
        valid_fields = ['title', 'publication_year', 'author__name', '-title', 
                       '-publication_year', '-author__name']
        
        if ordering:
            # Filter out invalid fields
            ordering = [field for field in ordering if field.lstrip('-') in 
                       [f.lstrip('-') for f in valid_fields]]
        
        return ordering
    
    def get_valid_fields(self, queryset, view, context={}):
        """
        Define valid ordering fields.
        """
        return [
            ('title', 'Book Title'),
            ('publication_year', 'Publication Year'),
            ('author__name', 'Author Name'),
            ('-title', 'Book Title (descending)'),
            ('-publication_year', 'Publication Year (descending)'),
            ('-author__name', 'Author Name (descending)'),
        ]
