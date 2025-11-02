# RETRIEVE
from bookshelf.models import Book
books = Book.objects.all()
books

# Expected Output:
<QuerySet [<Book: 1984 by George Orwell (1949)>]>
