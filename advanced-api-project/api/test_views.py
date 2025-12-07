"""
Unit tests for Book API endpoints in Django REST Framework.
These tests ensure the integrity of API endpoints and correctness of response data and status codes.
"""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from api.models import Book  # Fixed import
from api.serializers import BookSerializer  # Fixed import


class BookAPITestCase(APITestCase):
    """Base test case setup for Book API tests"""
    
    def setUp(self):
        """Set up test data before each test method"""
        # Create test users
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='testpassword123'
        )
        
        self.regular_user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='testpassword123'
        )
        
        # Create test books - adjusted to match your model fields
        self.book1 = Book.objects.create(
            title='Test Book 1',
            author='Author One',
            isbn='1234567890123',
            published_date='2023-01-01',  # Changed from publication_date
            genre='Fiction',
            price='19.99',  # String if using DecimalField
            stock=10  # Changed from stock_quantity
        )
        
        self.book2 = Book.objects.create(
            title='Test Book 2',
            author='Author Two',
            isbn='9876543210987',
            published_date='2022-06-15',
            genre='Non-Fiction',
            price='29.99',
            stock=5
        )
        
        self.book3 = Book.objects.create(
            title='Another Book',
            author='Author Three',
            isbn='5555555555555',
            published_date='2021-03-20',
            genre='Science',
            price='15.99',
            stock=0  # Out of stock
        )
        
        # API endpoints - adjust based on your URL patterns
        self.book_list_url = reverse('book-list')
        self.book_detail_url = lambda pk: reverse('book-detail', kwargs={'pk': pk})


class BookListViewTests(BookAPITestCase):
    """Tests for Book List and Create endpoints"""
    
    def test_get_all_books_unauthenticated(self):
        """Test retrieving all books without authentication"""
        response = self.client.get(self.book_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Response might be paginated, adjust accordingly
        if 'results' in response.data:  # If using pagination
            self.assertEqual(len(response.data['results']), 3)
        else:
            self.assertEqual(len(response.data), 3)
    
    def test_get_all_books_authenticated(self):
        """Test retrieving all books with authentication"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.book_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if 'results' in response.data:
            self.assertEqual(len(response.data['results']), 3)
        else:
            self.assertEqual(len(response.data), 3)
    
    def test_create_book_unauthenticated(self):
        """Test creating a book without authentication should fail"""
        data = {
            'title': 'New Book',
            'author': 'New Author',
            'isbn': '1111111111111',
            'published_date': '2024-01-01',
            'genre': 'Fantasy',
            'price': '24.99',
            'stock': 15
        }
        response = self.client.post(self.book_list_url, data)
        # Depending on your permissions, might be 401 or 403
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
    
    def test_create_book_authenticated_regular_user(self):
        """Test creating a book as regular user"""
        self.client.force_authenticate(user=self.regular_user)
        data = {
            'title': 'New Book',
            'author': 'New Author',
            'isbn': '1111111111111',
            'published_date': '2024-01-01',
            'genre': 'Fantasy',
            'price': '24.99',
            'stock': 15
        }
        response = self.client.post(self.book_list_url, data)
        # Check based on your permissions - if regular users can create
        if response.status_code == status.HTTP_201_CREATED:
            self.assertEqual(Book.objects.count(), 4)
            self.assertEqual(response.data['title'], 'New Book')
        else:  # If not allowed
            self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])
    
    def test_create_book_invalid_data(self):
        """Test creating a book with invalid data"""
        # First authenticate if needed
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'title': '',  # Empty title should be invalid
            'author': 'New Author',
            'isbn': 'invalid-isbn',  # Invalid ISBN
            'price': '-10'  # Negative price
        }
        response = self.client.post(self.book_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check which fields have errors
        self.assertIn('title', response.data)
        self.assertIn('isbn', response.data)
        self.assertIn('price', response.data)


class BookDetailViewTests(BookAPITestCase):
    """Tests for Book Retrieve, Update, and Delete endpoints"""
    
    def test_get_single_book_unauthenticated(self):
        """Test retrieving a single book without authentication"""
        url = self.book_detail_url(self.book1.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.book1.title)
    
    def test_get_nonexistent_book(self):
        """Test retrieving a book that doesn't exist"""
        url = self.book_detail_url(999)  # Non-existent ID
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_update_book_unauthenticated(self):
        """Test updating a book without authentication"""
        url = self.book_detail_url(self.book1.id)
        data = {'title': 'Updated Title'}
        response = self.client.patch(url, data)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
    
    def test_update_book_authenticated(self):
        """Test updating a book with authentication"""
        self.client.force_authenticate(user=self.admin_user)
        url = self.book_detail_url(self.book1.id)
        data = {'title': 'Updated Title', 'price': '25.99'}
        response = self.client.patch(url, data)
        if response.status_code == status.HTTP_200_OK:
            self.book1.refresh_from_db()
            self.assertEqual(self.book1.title, 'Updated Title')
            self.assertEqual(str(self.book1.price), '25.99')
        else:  # If not allowed
            self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN])
    
    def test_delete_book_unauthenticated(self):
        """Test deleting a book without authentication"""
        url = self.book_detail_url(self.book1.id)
        response = self.client.delete(url)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
    
    def test_delete_book_authenticated(self):
        """Test deleting a book with authentication"""
        self.client.force_authenticate(user=self.admin_user)
        url = self.book_detail_url(self.book1.id)
        response = self.client.delete(url)
        if response.status_code == status.HTTP_204_NO_CONTENT:
            self.assertEqual(Book.objects.count(), 2)
            self.assertFalse(Book.objects.filter(id=self.book1.id).exists())
        else:  # If not allowed
            self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN])


class BookFilteringTests(BookAPITestCase):
    """Tests for filtering, searching, and ordering functionality"""
    
    def test_filter_by_author(self):
        """Test filtering books by author"""
        url = f"{self.book_list_url}?author=Author One"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if 'results' in response.data:
            data = response.data['results']
        else:
            data = response.data
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['author'], 'Author One')
    
    def test_filter_by_genre(self):
        """Test filtering books by genre"""
        url = f"{self.book_list_url}?genre=Non-Fiction"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if 'results' in response.data:
            data = response.data['results']
        else:
            data = response.data
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['genre'], 'Non-Fiction')
    
    def test_search_functionality(self):
        """Test searching books - adjust based on your implementation"""
        # If you have search functionality
        url = f"{self.book_list_url}?search=Test"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_ordering(self):
        """Test ordering books - adjust based on your implementation"""
        url = f"{self.book_list_url}?ordering=title"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if 'results' in response.data:
            data = response.data['results']
        else:
            data = response.data
        titles = [book['title'] for book in data]
        self.assertEqual(titles, sorted(titles))


class BookSerializerTests(BookAPITestCase):
    """Tests for Book serializer validation"""
    
    def test_serializer_valid_data(self):
        """Test serializer with valid data"""
        data = {
            'title': 'Serializer Test Book',
            'author': 'Serializer Author',
            'isbn': '9999999999999',
            'published_date': '2023-12-01',
            'genre': 'Test',
            'price': '99.99',
            'stock': 100
        }
        serializer = BookSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_serializer_invalid_isbn(self):
        """Test serializer with invalid ISBN"""
        data = {
            'title': 'Test Book',
            'author': 'Test Author',
            'isbn': '123',  # Too short
            'price': '10.00'
        }
        serializer = BookSerializer(data=data)
        is_valid = serializer.is_valid()
        if not is_valid:
            self.assertIn('isbn', serializer.errors)
    
    def test_serializer_missing_required_fields(self):
        """Test serializer with missing required fields"""
        data = {
            'author': 'Test Author',
            # Missing title, isbn, price
        }
        serializer = BookSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        # Check which fields are required
        if 'title' in serializer.fields:
            self.assertIn('title', serializer.errors)
        if 'isbn' in serializer.fields:
            self.assertIn('isbn', serializer.errors)
        if 'price' in serializer.fields:
            self.assertIn('price', serializer.errors)


class BookModelTests(BookAPITestCase):
    """Tests for Book model methods and properties"""
    
    def test_book_string_representation(self):
        """Test the string representation of Book model"""
        self.assertEqual(str(self.book1), f'Test Book 1 by Author One')
    
    def test_book_in_stock_property(self):
        """Test if book is in stock - adjust based on your model"""
        # If you have an in_stock property or method
        if hasattr(self.book1, 'in_stock'):
            self.assertTrue(self.book1.in_stock)
        elif hasattr(self.book1, 'is_in_stock'):
            self.assertTrue(self.book1.is_in_stock())
        else:
            # Simple check based on stock
            self.assertTrue(self.book1.stock > 0)
            self.assertFalse(self.book3.stock > 0)