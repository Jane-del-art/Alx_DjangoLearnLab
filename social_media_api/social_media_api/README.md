## Social Media API
A Django REST API that supports user registration, login, and profile management using token authentication.

### Authentication Endpoints
- POST /api/accounts/register/
- POST /api/accounts/login/
- GET /api/accounts/profile/

## Follow System
POST /api/accounts/follow/<user_id>/
POST /api/accounts/unfollow/<user_id>/

## Feed
GET /api/feed/
Returns posts from users the authenticated user follows.
