from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.urls import reverse

# Import models and forms - CRITICAL: This line must exist!
from .models import Book
from .forms import ExampleForm, BookForm, SecureSearchForm

# ========================
# EXAMPLE FORM VIEW (for security demonstration)
# ========================
@login_required
def example_form_view(request):
    """
    View demonstrating secure form handling with ExampleForm.
    Includes CSRF protection, input validation, and sanitization.
    """
    if request.method == 'POST':
        form = ExampleForm(request.POST)
        if form.is_valid():
            # Form is valid - process the data securely
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            age = form.cleaned_data.get('age')
            message = form.cleaned_data['message']
            
            # In a real application, you would save to database here
            # For demonstration, we'll just show a success message
            
            # Always use cleaned_data from forms, never request.POST directly
            context = {
                'success': True,
                'name': name,
                'email': email,
                'age': age,
                'message': message[:100] + '...' if len(message) > 100 else message,
            }
            return render(request, 'bookshelf/example_form_success.html', context)
    else:
        form = ExampleForm()
    
    return render(request, 'bookshelf/example_form.html', {'form': form})

# ========================
# EXISTING VIEWS (updated with forms)
# ========================

# View for listing books - requires can_view_book permission
@permission_required('bookshelf.can_view_book', raise_exception=True)
def book_list(request):
    # Secure search functionality using Django ORM to prevent SQL injection
    search_query = request.GET.get('search', '').strip()
    
    if search_query:
        # Use Django's Q objects for safe query construction
        books = Book.objects.filter(
            Q(title__icontains=search_query) | Q(author__icontains=search_query)
        )
    else:
        books = Book.objects.all()
    
    context = {
        'books': books,
        'search_query': search_query,
    }
    return render(request, 'bookshelf/book_list.html', context)

# View for creating books - uses form validation
@permission_required('bookshelf.can_create_book', raise_exception=True)
def create_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            # Form validation handles all input sanitization
            form.save()
            return redirect('bookshelf:book_list')
    else:
        form = BookForm()
    
    return render(request, 'bookshelf/book_form.html', {'form': form})

# View for editing books - uses form validation
@permission_required('bookshelf.can_edit_book', raise_exception=True)
def edit_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('bookshelf:book_list')
    else:
        form = BookForm(instance=book)
    
    return render(request, 'bookshelf/book_form.html', {'form': form})

# View for deleting books
@permission_required('bookshelf.can_delete_book', raise_exception=True)
def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    
    if request.method == 'POST':
        book.delete()
        return redirect('bookshelf:book_list')
    
    return render(request, 'bookshelf/book_confirm_delete.html', {'book': book})

# View for book details
@permission_required('bookshelf.can_view_book', raise_exception=True)
def book_detail(request, book_id):
    # Use get_object_or_404 to prevent information disclosure
    book = get_object_or_404(Book, id=book_id)
    return render(request, 'bookshelf/book_detail.html', {'book': book})

# Secure search view using Django Forms
def secure_search(request):
    """
    Example of a secure search view that validates input using SecureSearchForm
    """
    results = []
    form = SecureSearchForm(request.GET or None)
    
    if form.is_valid():
        query = form.cleaned_data['query']
        
        if query:
            # Use Django ORM with parameterized queries (implicitly safe)
            results = Book.objects.filter(
                Q(title__icontains=query) | Q(author__icontains=query)
            )[:50]  # Limit results to prevent DoS
    
    return render(request, 'bookshelf/search.html', {
        'form': form,
        'results': results,
        'query': form.cleaned_data.get('query', '') if form.is_bound else ''
    })

# ========================
# DEMONSTRATION VIEW FOR SECURITY FEATURES
# ========================
def security_demo(request):
    """
    View to demonstrate various security features implemented.
    """
    context = {
        'csrf_enabled': True,
        'xss_protection': True,
        'sql_injection_prevention': True,
        'csp_enabled': True,
        'secure_cookies': True,
        'input_validation': True,
    }
    return render(request, 'bookshelf/security_demo.html', context)
