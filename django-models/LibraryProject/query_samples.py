import django
import os

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LibraryProject.settings')  # adjust if needed
django.setup()

from relationship_app.models import Author, Book, Library, Librarian

# Helper to create or get objects
def get_or_create_author(name):
    return Author.objects.get_or_create(name=name)[0]

def get_or_create_book(title, author):
    return Book.objects.get_or_create(title=title, author=author)[0]

def get_or_create_library(name):
    return Library.objects.get_or_create(name=name)[0]

def get_or_create_librarian(name, library):
    return Librarian.objects.get_or_create(name=name, library=library)[0]

# Create sample data safely
def create_sample_data():
    author1 = get_or_create_author("Chinua Achebe")
    author2 = get_or_create_author("Ngugi wa Thiong'o")

    book1 = get_or_create_book("Things Fall Apart", author1)
    book2 = get_or_create_book("Arrow of God", author1)
    book3 = get_or_create_book("Petals of Blood", author2)

    lib1 = get_or_create_library("National Library")
    lib2 = get_or_create_library("City Library")

    lib1.books.add(book1, book3)
    lib2.books.add(book2, book3)

    get_or_create_librarian("Grace", lib1)
    get_or_create_librarian("John", lib2)

# Print summary neatly
def print_summary():
    print("\n=== AUTHORS & BOOKS ===")
    for author in Author.objects.all():
        books = [book.title for book in author.book_set.all()]
        print(f"{author.name}: {books}")

    print("\n=== LIBRARIES & BOOKS & LIBRARIANS ===")
    for library in Library.objects.all():
        books = [book.title for book in library.books.all()]
        librarian = getattr(library, 'librarian', None)
        librarian_name = librarian.name if librarian else "No librarian"
        print(f"{library.name}: Books {books}, Librarian: {librarian_name}")

    print("\n=== LIBRARIANS & LIBRARIES ===")
    for librarian in Librarian.objects.all():
        print(f"{librarian.name}: Library {librarian.library.name}")

if __name__ == "__main__":
    create_sample_data()  # Safe: won’t create duplicates
    print_summary()
