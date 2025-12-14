from django.urls import path
from . import views

urlpatterns = [
    # Authentication endpoints
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    
    # User profile endpoints
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    
    # Password management
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    
    # Public user endpoints
    path('users/<str:username>/', views.UserDetailView.as_view(), name='user-detail'),
    path('users/<str:username>/follow/', views.FollowUserView.as_view(), name='follow-user'),
    path('users/<str:username>/followers/', views.FollowersListView.as_view(), name='user-followers'),
    path('users/<str:username>/following/', views.FollowingListView.as_view(), name='user-following'),
]
