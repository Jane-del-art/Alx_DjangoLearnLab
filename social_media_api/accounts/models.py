from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class User(AbstractUser):
    """Custom user model with additional fields for social media."""
    
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True,
        default='profile_pictures/default.png'
    )
    followers = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='following',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.username
    
    def follow(self, user):
        """Follow another user."""
        if user != self:
            self.following.add(user)
    
    def unfollow(self, user):
        """Unfollow a user."""
        if user != self:
            self.following.remove(user)
    
    @property
    def followers_count(self):
        """Return number of followers."""
        return self.followers.count()
    
    @property
    def following_count(self):
        """Return number of users this user is following."""
        return self.following.count()

class UserProfile(models.Model):
    """Extended profile information for users."""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    website = models.URLField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"