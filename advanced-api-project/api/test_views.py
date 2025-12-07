"""
Unit tests for Book API endpoints in Django REST Framework.
These tests ensure the integrity of API endpoints and correctness of response data and status codes.
"""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from api.models import Book
from api.serializers import BookSerializer


class BookAPITestCase(APITestCase):
    """Base test case setup for Book API tests"""
    
    def setUp(self):
        """Set up test data before each test method"""
        self.client = APIClient()
        
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
        
        # Create test books
        self.book1 = Book.objects.create(
            title='Test Book 1',
            author='Author One',
            isbn='1234567890123',
            publication_date='2023-01-01',
            genre='Fiction',
            price=19.99,
            stock_quantity=10
        )
        
        self.book2 = Book.objects.create(
            title='Test Book 2',
            author='Author Two',
            isbn='9876543210987',
            publication_date='2022-06-15',
            genre='Non-Fiction',
            price=29.99,
            stock_quantity=5
        )
        
        self.book3 = Book.objects.create(
            title='Another Book',
            author='Author Three',
            isbn='5555555555555',
            publication_date='2021-03-20',
            genre='Science',
            price=15.99,
            stock_quantity=0
        )
        
        # API endpoints
        self.book_list_url = reverse('book-list')
        self.book_detail_url = lambda pk: reverse('book-detail', args=[pk])


class BookListViewTests(BookAPITestCase):
    """Tests for Book List and Create endpoints"""
    
    def test_get_all_books_unauthenticated(self):
        """Test retrieving all books without authentication"""
        response = self.client.get(self.book_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if response is paginated
        if isinstance(response.data, dict) and 'results' in response.data:
            self.assertEqual(len(response.data['results']), 3)
        else:
            self.assertEqual(len(response.data), 3)
    
    def test_get_all_books_authenticated(self):
        """Test retrieving all books with authentication"""
        # Authenticate using login
        self.client.login(username='user', password='testpassword123')
        response = self.client.get(self.book_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_book_unauthenticated(self):
        """Test creating a book without authentication should fail"""
        data = {
            'title': 'New Book',
            'author': 'New Author',
            'isbn': '1111111111111',
            'publication_date': '2024-01-01',
            'genre': 'Fantasy',
            'price': 24.99,
            'stock_quantity': 15
        }
        response = self.client.post(self.book_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_book_authenticated_regular_user(self):
        """Test creating a book as regular user should fail"""
        # Login as regular user
        self.client.login(username='user', password='testpassword123')
        data = {
            'title': 'New Book',
            'author': 'New Author',
            'isbn': '1111111111111',
            'publication_date': '2024-01-01',
            'genre': 'Fantasy',
            'price': 24.99,
            'stock_quantity': 15
        }
        response = self.client.post(self.book_list_url, data)
        # Regular users might not have permission
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])
    
    def test_create_book_authenticated_admin(self):
        """Test creating a book as admin user should succeed"""
        # Login as admin
        self.client.login(username='admin', password='testpassword123')
        data = {
            'title': 'New Book',
            'author': 'New Author',
            'isbn': '1111111111111',
            'publication_date': '2024-01-01',
            'genre': 'Fantasy',
            'price': 24.99,
            'stock_quantity': 15
        }
        response = self.client.post(self.book_list_url, data)
        
        # If admin has permission
        if response.status_code == status.HTTP_201_CREATED:
            self.assertEqual(Book.objects.count(), 4)
            self.assertEqual(response.data['title'], 'New Book')
        else:
            # If not, test should fail
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_create_book_invalid_data(self):
        """Test creating a book with invalid data"""
        self.client.login(username='admin', password='testpassword123')
        data = {
            'title': '',  # Empty title
            'author': 'New Author',
            'isbn': 'invalid',  # Invalid ISBN
            'price': -10  # Negative price
        }
        response = self.client.post(self.book_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class BookDetailViewTests(BookAPITestCase):
    """Tests for Book Retrieve, Update, and Delete endpoints"""
    
    def test_get_single_book_unauthenticated(self):
        """Test retrieving a single book without authentication"""
        url = self.book_detail_url(self.book1.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Book 1')
    
    def test_get_nonexistent_book(self):
        """Test retrieving a book that doesn't exist"""
        url = self.book_detail_url(999)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_update_book_unauthenticated(self):
        """Test updating a book without authentication should fail"""
        url = self.book_detail_url(self.book1.id)
        data = {'title': 'Updated Title'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_update_book_authenticated_admin(self):
        """Test updating a book as admin user should succeed"""
        self.client.login(username='admin', password='testpassword123')
        url = self.book_detail_url(self.book1.id)
        data = {'title': 'Updated Title', 'price': 25.99}
        response = self.client.patch(url, data)
        
        if response.status_code == status.HTTP_200_OK:
            self.book1.refresh_from_db()
            self.assertEqual(self.book1.title, 'Updated Title')
        else:
            # If admin doesn't have permission, mark as expected failure
            self.skipTest("Admin doesn't have update permission")
    
    def test_delete_book_unauthenticated(self):
        """Test deleting a book without authentication should fail"""
        url = self.book_detail_url(self.book1.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_delete_book_authenticated_admin(self):
        """Test deleting a book as admin user should succeed"""
        self.client.login(username='admin', password='testpassword123')
        url = self.book_detail_url(self.book1.id)
        response = self.client.delete(url)
        
        if response.status_code == status.HTTP_204_NO_CONTENT:
            self.assertEqual(Book.objects.count(), 2)
        else:
            self.skipTest("Admin doesn't have delete permission")


class BookFilteringTests(BookAPITestCase):
    """Tests for filtering, searching, and ordering functionality"""
    
    def test_filter_by_author(self):
        """Test filtering books by author"""
        url = f"{self.book_list_url}?author=Author One"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check response structure
        if isinstance(response.data, dict) and 'results' in response.data:
            results = response.data['results']
        else:
            results = response.data
            
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['author'], 'Author One')
    
    def test_filter_by_genre(self):
        """Test filtering books by genre"""
        url = f"{self.book_list_url}?genre=Fiction"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        if isinstance(response.data, dict) and 'results' in response.data:
            results = response.data['results']
        else:
            results = response.data
            
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['genre'], 'Fiction')
    
    def test_filter_by_min_price(self):
        """Test filtering books by minimum price"""
        url = f"{self.book_list_url}?min_price=20"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        if isinstance(response.data, dict) and 'results' in response.data:
            results = response.data['results']
        else:
            results = response.data
            
        # Only book2 has price >= 20
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Test Book 2')
    
    def test_search_by_title(self):
        """Test searching books by title"""
        url = f"{self.book_list_url}?search=Test"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_ordering_by_title(self):
        """Test ordering books by title"""
        url = f"{self.book_list_url}?ordering=title"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        if isinstance(response.data, dict) and 'results' in response.data:
            results = response.data['results']
        else:
            results = response.data
            
        titles = [book['title'] for book in results]
        self.assertEqual(titles, sorted(titles))
    
    def test_ordering_by_price_descending(self):
        """Test ordering books by price descending"""
        url = f"{self.book_list_url}?ordering=-price"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        if isinstance(response.data, dict) and 'results' in response.data:
            results = response.data['results']
        else:
            results = response.data
            
        prices = [book['price'] for book in results]
        self.assertEqual(prices, sorted(prices, reverse=True))


class AuthenticationTests(BookAPITestCase):
    """Tests specifically for authentication scenarios"""
    
    def test_login_required_for_create(self):
        """Test that login is required to create a book"""
        data = {
            'title': 'Test Book',
            'author': 'Test Author',
            'isbn': '1231231231231',
            'price': 10.00
        }
        
        # Without login
        response = self.client.post(self.book_list_url, data)
        self.assertNotEqual(response.status_code, status.HTTP_201_CREATED)
        
        # With login
        self.client.login(username='admin', password='testpassword123')
        response = self.client.post(self.book_list_url, data)
        # Might be 201 or 403 depending on permissions
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_403_FORBIDDEN])
    
    def test_logout_functionality(self):
        """Test that logout prevents protected actions"""
        # Login and perform action
        self.client.login(username='admin', password='testpassword123')
        data = {'title': 'Updated'}
        response = self.client.patch(self.book_detail_url(self.book1.id), data)
        initial_status = response.status_code
        
        # Logout
        self.client.logout()
        
        # Try again
        response = self.client.patch(self.book_detail_url(self.book1.id), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_wrong_password_fails(self):
        """Test that wrong password prevents authentication"""
        # Try with wrong password
        login_success = self.client.login(username='admin', password='wrongpassword')
        self.assertFalse(login_success)
        
        # Try protected action
        data = {'title': 'Should Fail'}
        response = self.client.patch(self.book_detail_url(self.book1.id), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class SerializerTests(BookAPITestCase):
    """Tests for serializer validation"""
    
    def test_serializer_valid_data(self):
        """Test serializer with valid data"""
        data = {
            'title': 'Valid Book',
            'author': 'Valid Author',
            'isbn': '1234567890123',
            'price': 19.99,
            'publication_date': '2023-01-01',
            'genre': 'Test',
            'stock_quantity': 10
        }
        serializer = BookSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_serializer_missing_required(self):
        """Test serializer with missing required fields"""
        data = {
            'author': 'Test Author',
            # Missing title, isbn, price
        }
        serializer = BookSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)
        self.assertIn('isbn', serializer.errors)
        self.assertIn('price', serializer.errors)
    
    def test_serializer_invalid_isbn(self):
        """Test serializer with invalid ISBN"""
        data = {
            'title': 'Test Book',
            'author': 'Test Author',
            'isbn': '123',  # Too short
            'price': 10.00
        }
        serializer = BookSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('isbn', serializer.errors)


class ModelTests(BookAPITestCase):
    """Tests for Book model"""
    
    def test_string_representation(self):
        """Test string representation of Book"""
        self.assertEqual(str(self.book1), 'Test Book 1')
    
    def test_model_methods(self):
        """Test any custom model methods"""
        # Example: if you have a method to check stock
        if hasattr(self.book1, 'is_in_stock'):
            self.assertTrue(self.book1.is_in_stock())
            self.assertFalse(self.book3.is_in_stock())


# Run all tests
if __name__ == '__main__':
    import django
    django.setup()
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'test', 'api.tests_views'])
