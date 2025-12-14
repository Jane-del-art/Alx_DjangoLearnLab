from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from .models import User, UserProfile

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(write_only=True, min_length=6, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, min_length=6, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name']
        extra_kwargs = {
            'email': {'required': True}
        }
    
    def validate_email(self, value):
        """Validate email uniqueness."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def validate_username(self, value):
        """Validate username uniqueness."""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value
    
    def validate(self, data):
        """Validate that passwords match."""
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Passwords must match."})
        return data
    
    def create(self, validated_data):
        """Create a new user."""
        # Remove password2 from validated data
        validated_data.pop('password2')
        
        # Get password
        password = validated_data.pop('password')
        
        # Create user instance
        user = User(**validated_data)
        user.set_password(password)  # Hash the password
        user.save()
        
        return user

class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    def validate(self, data):
        """Validate user credentials."""
        username = data.get('username')
        password = data.get('password')
        
        if username and password:
            # Try to authenticate with username or email
            user = None
            
            # Check if input is email
            if '@' in username:
                try:
                    user_obj = User.objects.get(email=username)
                    username = user_obj.username
                except User.DoesNotExist:
                    pass
            
            # Authenticate user
            user = authenticate(username=username, password=password)
            
            if user:
                if not user.is_active:
                    raise serializers.ValidationError("User account is disabled.")
                data['user'] = user
            else:
                raise serializers.ValidationError("Unable to log in with provided credentials.")
        else:
            raise serializers.ValidationError("Must include 'username' and 'password'.")
        
        return data

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile."""
    class Meta:
        model = UserProfile
        fields = ['website', 'location', 'birth_date']

class UserSerializer(serializers.ModelSerializer):
    """Serializer for user details."""
    profile = UserProfileSerializer(read_only=True)
    followers_count = serializers.IntegerField(read_only=True)
    following_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'bio', 'profile_picture', 'followers_count', 'following_count',
            'profile', 'created_at', 'is_active'
        ]
        read_only_fields = ['id', 'created_at', 'is_active']
        extra_kwargs = {
            'email': {'read_only': True}
        }

class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user information."""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'bio', 'profile_picture']

class UserPasswordChangeSerializer(serializers.Serializer):
    """Serializer for changing user password."""
    old_password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})
    new_password = serializers.CharField(required=True, write_only=True, min_length=6, style={'input_type': 'password'})
    confirm_password = serializers.CharField(required=True, write_only=True, min_length=6, style={'input_type': 'password'})
    
    def validate_old_password(self, value):
        """Validate old password."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value
    
    def validate(self, data):
        """Validate that new passwords match."""
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"new_password": "New passwords must match."})
        return data
    
    def save(self, **kwargs):
        """Save new password."""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user

class FollowerSerializer(serializers.ModelSerializer):
    """Serializer for followers/following."""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'profile_picture']
