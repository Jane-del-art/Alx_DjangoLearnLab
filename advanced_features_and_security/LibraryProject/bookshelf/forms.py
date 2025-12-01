from django import forms
from django.core.exceptions import ValidationError
from .models import Book

# ========================
# EXAMPLE FORM 
# ========================
class ExampleForm(forms.Form):
    """
    Example form demonstrating secure form practices.
    This form includes various security features and input validation.
    """
    
    name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your name'
        }),
        help_text="Enter your full name (max 100 characters)"
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'email@example.com'
        }),
        help_text="Enter a valid email address"
    )
    
    age = forms.IntegerField(
        required=False,
        min_value=0,
        max_value=150,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Age (optional)'
        }),
        help_text="Enter your age (0-150)"
    )
    
    message = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Enter your message here...',
            'maxlength': '1000'
        }),
        help_text="Enter your message (max 1000 characters)"
    )
    
    agree_to_terms = forms.BooleanField(
        required=True,
        label="I agree to the terms and conditions",
        help_text="You must agree to the terms to submit this form"
    )
    
    def clean_name(self):
        """Validate name field with security checks."""
        name = self.cleaned_data['name'].strip()
        
        # Check minimum length
        if len(name) < 2:
            raise ValidationError("Name must be at least 2 characters long.")
        
        # Check for potentially dangerous content (XSS prevention)
        dangerous_patterns = [
            '<script>', '</script>', 'javascript:', 'onload=', 'onerror=',
            'onclick=', 'onmouseover=', 'eval(', 'alert('
        ]
        
        for pattern in dangerous_patterns:
            if pattern.lower() in name.lower():
                raise ValidationError("Name contains potentially dangerous content.")
        
        return name
    
    def clean_message(self):
        """Validate message field with security checks."""
        message = self.cleaned_data['message'].strip()
        
        # Check minimum length
        if len(message) < 10:
            raise ValidationError("Message must be at least 10 characters long.")
        
        # Limit maximum length to prevent DoS
        if len(message) > 1000:
            raise ValidationError("Message is too long (max 1000 characters).")
        
        # Sanitize potentially dangerous content
        import re
        # Remove script tags and event handlers
        message = re.sub(r'<script.*?>.*?</script>', '', message, flags=re.IGNORECASE)
        message = re.sub(r'on\w+=".*?"', '', message, flags=re.IGNORECASE)
        message = re.sub(r'on\w+=\'.*?\'', '', message, flags=re.IGNORECASE)
        
        return message
    
    def clean(self):
        """Additional cross-field validation."""
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        age = cleaned_data.get('age')
        
        # Example: If age is provided, ensure name is not just initials
        if age and name:
            if len(name.split()) < 2 and age > 18:
                self.add_error('name', "Adults should provide full name")
        
        return cleaned_data

# ========================
# BOOK FORM (for Book model)
# ========================
class BookForm(forms.ModelForm):
    """Form for creating and editing books with validation."""
    
    class Meta:
        model = Book
        fields = ['title', 'author', 'publication_year']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '200',
                'placeholder': 'Book Title'
            }),
            'author': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '100',
                'placeholder': 'Author Name'
            }),
            'publication_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '2100',
                'placeholder': 'Publication Year'
            }),
        }
        help_texts = {
            'title': 'Enter the book title (max 200 characters)',
            'author': 'Enter the author name (max 100 characters)',
            'publication_year': 'Enter the publication year (0-2100)',
        }
    
    def clean_title(self):
        """Validate book title."""
        title = self.cleaned_data['title'].strip()
        
        if len(title) < 2:
            raise ValidationError("Title must be at least 2 characters long.")
        
        # Security check for potentially dangerous content
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

# ========================
# SEARCH FORM
# ========================
class SecureSearchForm(forms.Form):
    """
    Secure search form with input validation to prevent SQL injection.
    """
    
    query = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search books...',
            'maxlength': '100'
        }),
        help_text="Enter search term (max 100 characters)"
    )
    
    def clean_query(self):
        """Clean and validate search query."""
        query = self.cleaned_data['query'].strip()
        
        # Check for minimum length
        if len(query) < 1:
            raise ValidationError("Search query cannot be empty.")
        
        # Security: Remove potentially dangerous characters
        import re
        # Allow only alphanumeric, spaces, hyphens, and apostrophes
        query = re.sub(r'[^\w\s\-\']', '', query)
        
        # Check for SQL injection patterns (additional safety)
        sql_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'SELECT', 'UNION', '--']
        for keyword in sql_keywords:
            if keyword.lower() in query.lower():
                raise ValidationError("Search query contains invalid characters.")
        
        return query
