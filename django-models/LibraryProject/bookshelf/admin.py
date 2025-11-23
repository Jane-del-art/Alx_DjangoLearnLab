from django.contrib import admin
from .models import Book

# Register the Book model with custom admin options
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publication_year')  # shows these columns in the admin list view
    search_fields = ('title', 'author')                     # enables search bar for title and author
    list_filter = ('publication_year',)                     # adds a filter sidebar for publication year
