# API Testing Documentation

## Overview
This document describes the unit testing strategy for the Book API endpoints in the Django REST Framework project.

## Test Structure

### Test Files
- `/api/test_views.py`: Contains all unit tests for API endpoints
- Uses Django's built-in test framework based on Python's unittest module

### Test Classes
1. **BookAPITestCase**: Base test case with common setup
2. **BookListViewTests**: Tests for list and create endpoints
3. **BookDetailViewTests**: Tests for retrieve, update, and delete endpoints
4. **BookFilteringTests**: Tests for filtering, searching, and ordering
5. **BookSerializerTests**: Tests for serializer validation
6. **BookModelTests**: Tests for model methods

## Test Coverage

### Authentication & Permissions
- Unauthenticated access to protected endpoints
- Regular user access to admin-only endpoints
- Admin user access to all endpoints

### CRUD Operations
- Create: Valid and invalid data, authentication requirements
- Read: Single and multiple records, non-existent records
- Update: Partial and full updates, authentication requirements
- Delete: Authentication requirements, data removal

### Filtering & Searching
- Filter by: author, genre, price range, stock availability
- Search by: title, author
- Ordering by: title, price, publication date (ascending/descending)
- Combined filters

### Data Validation
- ISBN format validation
- Price validation (non-negative)
- Required field validation
- Data type validation

## Running Tests

### Basic Commands
```bash
# Run all tests
python manage.py test api

# Run with verbosity
python manage.py test api -v 2

# Run specific test class
python manage.py test api.tests_views.BookListViewTests

# Run specific test method
python manage.py test api.tests_views.BookListViewTests.test_create_book_authenticated_admin