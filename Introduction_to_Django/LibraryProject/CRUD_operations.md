# CRUD Operations on the Book Model

# CREATE
from bookshelf.models import Book
book = Book.objects.create(title="1984", author="George Orwell", publication_year=1949)
book

# Output:
<Book: 1984 by George Orwell (1949)>

# RETRIEVE
from bookshelf.models import Book
books = Book.objects.all()
books

# Output:
<QuerySet [<Book: 1984 by George Orwell (1949)>]>

# UPDATE
from bookshelf.models import Book
book = Book.objects.get(title="1984")
book.title = "Nineteen Eighty-Four"
book.save()
book

# Output:
<Book: Nineteen Eighty-Four by George Orwell (1949)>

# DELETE
from bookshelf.models import Book
book = Book.objects.get(title="Nineteen Eighty-Four")
book.delete()
Book.objects.all()

# Output:
(1, {'bookshelf.Book': 1})
<QuerySet []>
