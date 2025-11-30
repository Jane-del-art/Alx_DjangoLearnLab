from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView
from django.contrib.auth import login  
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import user_passes_test, permission_required
from .models import Book, Library, Author
from django.contrib.auth import get_user_model

# Get the custom user model
User = get_user_model()

def list_books(request):
    books = Book.objects.all()
    return render(request, 'relationship_app/list_books.html', {'books': books})

class LibraryDetailView(DetailView):
    model = Library
    template_name = 'relationship_app/library_detail.html'
    context_object_name = 'library'

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('list_books')
    else:
        form = UserCreationForm()
    return render(request, 'relationship_app/register.html', {'form': form})

# UPDATED ROLE CHECK FUNCTIONS - Using Django's built-in permissions
def is_admin(user):
    return user.is_authenticated and user.is_staff

def is_librarian(user):
    return user.is_authenticated and user.groups.filter(name='Librarian').exists()

def is_member(user):
    return user.is_authenticated and user.is_active

# ROLE-BASED VIEWS
@user_passes_test(is_admin, login_url='/relationship_app/login/')
def admin_view(request):
    return render(request, 'relationship_app/admin_view.html')

@user_passes_test(is_librarian, login_url='/relationship_app/login/')
def librarian_view(request):
    return render(request, 'relationship_app/librarian_view.html')

@user_passes_test(is_member, login_url='/relationship_app/login/')
def member_view(request):
    return render(request, 'relationship_app/member_view.html')

# PERMISSION-BASED VIEWS FOR BOOK MANAGEMENT
@permission_required('relationship_app.add_book', login_url='/relationship_app/login/')
def add_book(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        author_name = request.POST.get('author')
        author, created = Author.objects.get_or_create(name=author_name)
        Book.objects.create(title=title, author=author)
        return redirect('list_books')
    return render(request, 'relationship_app/add_book.html')

@permission_required('relationship_app.change_book', login_url='/relationship_app/login/')
def edit_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        book.title = request.POST.get('title')
        author_name = request.POST.get('author')
        author, created = Author.objects.get_or_create(name=author_name)
        book.author = author
        book.save()
        return redirect('list_books')
    return render(request, 'relationship_app/edit_book.html', {'book': book})

@permission_required('relationship_app.delete_book', login_url='/relationship_app/login/')
def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        book.delete()
        return redirect('list_books')
    return render(request, 'relationship_app/delete_book.html', {'book': book})