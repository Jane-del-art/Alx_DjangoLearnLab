from django.contrib import admin
from .models import Author, Book

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for the Author model.
    """
    list_display = ('name', 'book_count')
    search_fields = ('name',)
    list_filter = ()
    
    def book_count(self, obj):
        """Display count of books for each author."""
        return obj.books.count()
    book_count.short_description = 'Number of Books'


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for the Book model.
    """
    list_display = ('title', 'author', 'publication_year')
    list_filter = ('author', 'publication_year')
    search_fields = ('title', 'author__name')
    raw_id_fields = ('author',)  # Better widget for foreign key
    ordering = ('-publication_year', 'title')