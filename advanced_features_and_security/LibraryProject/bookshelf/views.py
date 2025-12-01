from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q
from django.core.exceptions import ValidationError
from .models import Book
from .forms import BookForm  # We'll create this form for validation

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
    Example of a secure search view that validates input
    """
    results = []
    query = ''
    
    if request.method == 'GET':
        query = request.GET.get('q', '').strip()
        
        # Validate query length
        if len(query) > 100:
            raise ValidationError("Search query too long")
        
        # Sanitize query (remove potentially dangerous characters)
        import re
        query = re.sub(r'[^\w\s\-]', '', query)  # Allow only alphanumeric, spaces, and hyphens
        
        if query:
            # Use Django ORM with parameterized queries (implicitly safe)
            results = Book.objects.filter(
                Q(title__icontains=query) | Q(author__icontains=query)
            )[:50]  # Limit results to prevent DoS
    
    return render(request, 'bookshelf/search.html', {
        'results': results,
        'query': query
    })
