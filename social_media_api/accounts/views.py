from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth import login, logout
from django.contrib.auth import get_user_model
from .models import UserProfile
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserSerializer,
    UserUpdateSerializer,
    UserPasswordChangeSerializer,
    FollowerSerializer
)

User = get_user_model()

class UserRegistrationView(APIView):
    """View for user registration."""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Create user profile
            UserProfile.objects.create(user=user)
            
            # Create authentication token
            token = Token.objects.create(user=user)
            
            # Log the user in
            login(request, user)
            
            return Response({
                'message': 'User registered successfully!',
                'user': UserSerializer(user).data,
                'token': token.key
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    """View for user login."""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Log the user in
            login(request, user)
            
            # Get or create authentication token
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                'message': 'Login successful!',
                'user': UserSerializer(user).data,
                'token': token.key
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLogoutView(APIView):
    """View for user logout."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        # Delete the user's token
        try:
            request.user.auth_token.delete()
        except (AttributeError, Token.DoesNotExist):
            pass
        
        # Logout the user
        logout(request)
        
        return Response({
            'message': 'Logout successful!'
        }, status=status.HTTP_200_OK)

class UserProfileView(generics.RetrieveUpdateAPIView):
    """View for retrieving and updating user profile."""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = UserUpdateSerializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'message': 'Profile updated successfully!',
            'user': UserSerializer(instance).data
        }, status=status.HTTP_200_OK)

class UserDetailView(generics.RetrieveAPIView):
    """View for retrieving user details (public)."""
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'username'

class ChangePasswordView(APIView):
    """View for changing user password."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = UserPasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            user = serializer.save()
            
            # Delete old token and create new one for security
            try:
                Token.objects.filter(user=user).delete()
            except Token.DoesNotExist:
                pass
            
            # Create new token
            new_token = Token.objects.create(user=user)
            
            return Response({
                'message': 'Password changed successfully!',
                'token': new_token.key
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FollowUserView(APIView):
    """View for following/unfollowing users."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, username):
        try:
            user_to_follow = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if user_to_follow == request.user:
            return Response(
                {'error': 'You cannot follow yourself.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        current_user = request.user
        
        # Check if already following
        if current_user.following.filter(id=user_to_follow.id).exists():
            # Unfollow
            current_user.following.remove(user_to_follow)
            message = f'Unfollowed {username}'
            action = 'unfollowed'
        else:
            # Follow
            current_user.following.add(user_to_follow)
            message = f'Now following {username}'
            action = 'followed'
        
        return Response({
            'message': message,
            'action': action,
            'following_count': current_user.following.count(),
            'followers_count': current_user.followers.count(),
            'target_user_followers_count': user_to_follow.followers.count()
        }, status=status.HTTP_200_OK)

class FollowersListView(generics.ListAPIView):
    """View to list user's followers."""
    serializer_class = FollowerSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        username = self.kwargs.get('username')
        try:
            user = User.objects.get(username=username)
            return user.followers.all()
        except User.DoesNotExist:
            return User.objects.none()

class FollowingListView(generics.ListAPIView):
    """View to list who a user is following."""
    serializer_class = FollowerSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        username = self.kwargs.get('username')
        try:
            user = User.objects.get(username=username)
            return user.following.all()
        except User.DoesNotExist:
            return User.objects.none()
