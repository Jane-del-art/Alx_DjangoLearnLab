from rest_framework import generics, viewsets, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from .models import Book
from .serializers import BookSerializer

class BookList(generics.ListAPIView):
    """
    API endpoint that allows books to be viewed (original implementation).
    Now requires authentication to access.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]  # Allow read access to all, write only to authenticated

class BookViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling all CRUD operations on the Book model.
    
    Permissions:
    - IsAuthenticated: Users must be authenticated for all operations
    - IsAdminUser: Only admin users can delete books (custom permission)
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    
    # Set permission classes
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        """
        Override to use different permissions for different actions.
        """
        if self.action == 'destroy':
            # Only admin users can delete books
            return [permissions.IsAdminUser()]
        elif self.action in ['create', 'update', 'partial_update']:
            # Authenticated users can create and update
            return [permissions.IsAuthenticated()]
        else:
            # Anyone can view (list and retrieve)
            return [permissions.AllowAny()]
    
    def perform_create(self, serializer):
        """
        Override create to add custom logic if needed.
        """
        serializer.save()
    
    def perform_update(self, serializer):
        """
        Override update to add custom logic if needed.
        """
        serializer.save()
    
    def perform_destroy(self, instance):
        """
        Override destroy to add custom logic if needed.
        """
        instance.delete()

class CustomObtainAuthToken(ObtainAuthToken):
    """
    Custom authentication token view that returns additional user information.
    """
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'email': user.email,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'message': 'Token retrieved successfully. Use this token in the Authorization header as: Token <your_token>'
        })

# Custom permission classes
class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner
        return obj.owner == request.user

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow all users to read, but only admin to write.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to admin users
        return request.user and request.user.is_staff

class IsSuperUser(permissions.BasePermission):
    """
    Custom permission to only allow superusers.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser
