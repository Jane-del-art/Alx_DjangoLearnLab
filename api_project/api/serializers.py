from rest_framework import serializers
from .models import Book

class BookSerializer(serializers.ModelSerializer):
    """
    Serializer for the Book model.
    Converts Book model instances to JSON format and vice versa.
    """
    class Meta:
        model = Book
        fields = '__all__'  # Include all fields from the Book model
        # Alternatively, you can specify fields explicitly:
        # fields = ['id', 'title', 'author']