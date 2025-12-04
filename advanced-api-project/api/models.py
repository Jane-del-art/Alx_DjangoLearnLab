from django.db import models

class Author(models.Model):
    """
    Author model representing a book author.
    
    Fields:
    - name: CharField to store the author's full name
        - Max length: 100 characters
        - Required field
    
    Relationships:
    - Has a one-to-many relationship with Book model
      (One author can write multiple books)
    """
    name = models.CharField(max_length=100, help_text="Full name of the author")
    
    def __str__(self):
        """String representation of the Author model."""
        return self.name
    
    class Meta:
        """Metadata for the Author model."""
        verbose_name = "Author"
        verbose_name_plural = "Authors"
        ordering = ['name']  # Order authors alphabetically by name


class Book(models.Model):
    """
    Book model representing a published book.
    
    Fields:
    - title: CharField for the book's title
        - Max length: 200 characters
        - Required field
    
    - publication_year: IntegerField for the year of publication
        - Stores the year as an integer
        - Validated to ensure it's not in the future
    
    - author: ForeignKey linking to the Author model
        - Establishes a one-to-many relationship (Author → Books)
        - On delete: CASCADE (if author is deleted, their books are deleted)
        - Related name: 'books' (access an author's books via author.books.all())
    
    This model demonstrates:
    1. Foreign key relationship for data normalization
    2. Data validation for publication year
    3. Proper model relationships and database constraints
    """
    title = models.CharField(max_length=200, help_text="Title of the book")
    publication_year = models.IntegerField(help_text="Year the book was published")
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name='books',  # Allows reverse lookup: author.books.all()
        help_text="Author of the book"
    )
    
    def __str__(self):
        """String representation of the Book model."""
        return f"{self.title} ({self.publication_year})"
    
    class Meta:
        """Metadata for the Book model."""
        verbose_name = "Book"
        verbose_name_plural = "Books"
        ordering = ['title']  # Order books alphabetically by title
        # Ensure unique constraint: same title by same author in same year
        unique_together = ['title', 'author', 'publication_year']