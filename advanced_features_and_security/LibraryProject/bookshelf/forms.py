from django import forms
from django.core.exceptions import ValidationError
from .models import Book

class BookForm(forms.ModelForm):
    """Form for creating and editing books with validation."""
    
    class Meta:
        model = Book
        fields = ['title', 'author', 'publication_year']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '200'}),
            'author': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '100'}),
            'publication_year': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '2100'}),
        }
    
    def clean_title(self):
        """Validate book title."""
        title = self.cleaned_data['title'].strip()
        if len(title) < 2:
            raise ValidationError("Title must be at least 2 characters long.")
        
        # Check for potentially dangerous content
        dangerous_patterns = ['<script>', 'javascript:', 'onload=', 'onerror=']
        for pattern in dangerous_patterns:
            if pattern in title.lower():
                raise ValidationError("Title contains potentially dangerous content.")
        
        return title
    
    def clean_author(self):
        """Validate author name."""
        author = self.cleaned_data['author'].strip()
        if len(author) < 2:
            raise ValidationError("Author name must be at least 2 characters long.")
        return author
    
    def clean_publication_year(self):
        """Validate publication year."""
        year = self.cleaned_data['publication_year']
        current_year = 2025  # Update as needed
        
        if year < 0 or year > current_year:
            raise ValidationError(f"Publication year must be between 0 and {current_year}.")
        
        return year
