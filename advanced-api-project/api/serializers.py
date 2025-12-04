from rest_framework import serializers
from django.utils import timezone
from .models import Author, Book


class BookSerializer(serializers.ModelSerializer):
    """
    BookSerializer for serializing Book model instances.
    
    This serializer handles:
    1. All fields from the Book model (id, title, publication_year, author)
    2. Custom validation for publication_year
    3. Nested representation in AuthorSerializer
    
    Validation Rules:
    - publication_year must not be in the future
    - publication_year must be a reasonable year (between 0 and current year)
    """
    class Meta:
        model = Book
        fields = '__all__'  # Include all fields: id, title, publication_year, author
        read_only_fields = ('id',)  # ID is auto-generated
    
    def validate_publication_year(self, value):
        """
        Validate that the publication year is not in the future.
        
        Args:
            value (int): The publication year to validate
            
        Returns:
            int: The validated publication year
            
        Raises:
            serializers.ValidationError: If the year is in the future or invalid
        """
        current_year = timezone.now().year
        
        # Check if year is in the future
        if value > current_year:
            raise serializers.ValidationError(
                f"Publication year cannot be in the future. Current year is {current_year}."
            )
        
        # Check if year is reasonable (not before 0)
        if value < 0:
            raise serializers.ValidationError(
                "Publication year must be a positive number."
            )
        
        # Additional check: year should not be too far in the past
        # (Optional, adjust as needed for your use case)
        if value < 1000:
            raise serializers.ValidationError(
                "Publication year seems too far in the past. Please verify."
            )
        
        return value
    
    def validate(self, data):
        """
        Perform cross-field validation.
        
        This method validates relationships between fields.
        Example: Could check if the author has other books with same title in same year.
        
        Args:
            data (dict): The data to validate
            
        Returns:
            dict: The validated data
        """
        # You can add cross-field validation here
        # For example: Check if author already has a book with same title in same year
        title = data.get('title')
        publication_year = data.get('publication_year')
        author = data.get('author')
        
        if title and publication_year and author:
            # Check for existing books with same title, year, and author
            existing_books = Book.objects.filter(
                title=title,
                publication_year=publication_year,
                author=author
            )
            
            # If updating an existing instance, exclude it from the check
            if self.instance:
                existing_books = existing_books.exclude(pk=self.instance.pk)
            
            if existing_books.exists():
                raise serializers.ValidationError({
                    'title': f"Author '{author.name}' already has a book titled '{title}' published in {publication_year}."
                })
        
        return data


class AuthorSerializer(serializers.ModelSerializer):
    """
    AuthorSerializer for serializing Author model instances.
    
    This serializer demonstrates:
    1. Basic author information (id, name)
    2. Nested serialization of related books using BookSerializer
    3. Dynamic inclusion of related data
    
    The 'books' field uses BookSerializer to serialize all books
    written by the author, creating a nested JSON structure.
    """
    # Nested serializer for related books
    # Using many=True because an author can have multiple books
    books = BookSerializer(many=True, read_only=True, source='books.all')
    
    # Computed field example: total books count
    total_books = serializers.SerializerMethodField()
    
    class Meta:
        model = Author
        fields = ['id', 'name', 'books', 'total_books']  # Include nested books
        read_only_fields = ('id', 'books', 'total_books')
    
    def get_total_books(self, obj):
        """
        Compute and return the total number of books by this author.
        
        Args:
            obj (Author): The Author instance being serialized
            
        Returns:
            int: Number of books by this author
        """
        return obj.books.count()
    
    def validate_name(self, value):
        """
        Validate author name.
        
        Args:
            value (str): The author name to validate
            
        Returns:
            str: The validated author name
            
        Raises:
            serializers.ValidationError: If name is invalid
        """
        # Trim whitespace
        value = value.strip()
        
        # Check minimum length
        if len(value) < 2:
            raise serializers.ValidationError(
                "Author name must be at least 2 characters long."
            )
        
        # Check for valid characters (allow letters, spaces, hyphens, apostrophes)
        import re
        if not re.match(r'^[A-Za-z\s\-\'\.]+$', value):
            raise serializers.ValidationError(
                "Author name can only contain letters, spaces, hyphens, apostrophes, and periods."
            )
        
        return value


class AuthorDetailSerializer(AuthorSerializer):
    """
    Detailed AuthorSerializer with additional information.
    
    This extends the basic AuthorSerializer to include:
    1. More detailed book information
    2. Additional computed fields
    3. Different representation for detail views vs list views
    """
    # Example of a different nested representation for detail view
    books = BookSerializer(many=True, read_only=True)
    
    class Meta(AuthorSerializer.Meta):
        fields = AuthorSerializer.Meta.fields + ['created_at', 'updated_at']


class BookDetailSerializer(BookSerializer):
    """
    Detailed BookSerializer with nested author information.
    
    This serializer includes complete author information
    instead of just the author ID.
    """
    # Include complete author information (nested)
    author = AuthorSerializer(read_only=True)
    
    class Meta(BookSerializer.Meta):
        # Same fields as BookSerializer but with nested author
        fields = BookSerializer.Meta.fields