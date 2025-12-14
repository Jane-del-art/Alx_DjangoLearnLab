from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, UserProfile

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True}
        }

    def validate(self, attrs):
        """Validate that passwords match."""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

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

    def create(self, validated_data):
        """Create and return a new user."""
        # Remove password2 from validated data
        validated_data.pop('password2')
        
        # Get password
        password = validated_data.pop('password')
        
        # Create user instance
        user = User.objects.create(**validated_data)
        
        # Set password (hashed)
        user.set_password(password)
        user.save()
        
        return user

class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    username = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, data):
        """Validate user credentials."""
        username = data.get('username')
        password = data.get('password')

        if username and password:
            # Check if input is email
            if '@' in username:
                try:
                    user_obj = User.objects.get(email=username)
                    username = user_obj.username
                except User.DoesNotExist:
                    username = None

            # Authenticate user
            user = authenticate(username=username, password=password)
            
            if user:
                if not user.is_active:
                    raise serializers.ValidationError("User account is disabled.")
            else:
                raise serializers.ValidationError("Unable to log in with provided credentials.")
            
            data['user'] = user
        else:
            raise serializers.ValidationError("Must include 'username' and 'password'.")
        
        return data

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile."""
    class Meta:
        model = UserProfile
        fields = ['website', 'location', 'birth_date']
        read_only_fields = ['id']

class UserSerializer(serializers.ModelSerializer):
    """Serializer for user details."""
    profile = UserProfileSerializer(read_only=True)
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'bio', 'profile_picture', 'followers_count', 'following_count',
            'profile', 'date_joined', 'is_active'
        ]
        read_only_fields = ['id', 'date_joined', 'is_active', 'email']
        extra_kwargs = {
            'email': {'read_only': True}
        }

    def get_followers_count(self, obj):
        """Get number of followers."""
        return obj.followers.count()

    def get_following_count(self, obj):
        """Get number of users being followed."""
        return obj.following.count()

class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user information."""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'bio', 'profile_picture']
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'bio': {'required': False, 'allow_blank': True},
            'profile_picture': {'required': False}
        }

class UserPasswordChangeSerializer(serializers.Serializer):
    """Serializer for changing user password."""
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    confirm_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate_old_password(self, value):
        """Validate old password."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def validate(self, attrs):
        """Validate that new passwords match."""
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        return attrs

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

class UserMinimalSerializer(serializers.ModelSerializer):
    """Minimal user serializer for list views."""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'profile_picture']
