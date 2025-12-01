# LibraryProject/setup_permissions.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LibraryProject.settings')
django.setup()

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from bookshelf.models import Book

def setup_groups():
    # Get content type for Book model
    content_type = ContentType.objects.get_for_model(Book)
    
    # Create groups
    viewers_group, created = Group.objects.get_or_create(name='Viewers')
    editors_group, created = Group.objects.get_or_create(name='Editors')
    admins_group, created = Group.objects.get_or_create(name='Admins')
    
    # Assign permissions to Viewers group
    view_permission = Permission.objects.get_or_create(
        codename='can_view_book',
        content_type=content_type,
        defaults={'name': 'Can view book'}
    )[0]
    viewers_group.permissions.add(view_permission)
    
    # Assign permissions to Editors group
    create_permission = Permission.objects.get_or_create(
        codename='can_create_book',
        content_type=content_type,
        defaults={'name': 'Can create book'}
    )[0]
    edit_permission = Permission.objects.get_or_create(
        codename='can_edit_book',
        content_type=content_type,
        defaults={'name': 'Can edit book'}
    )[0]
    editors_group.permissions.add(view_permission, create_permission, edit_permission)
    
    # Assign all permissions to Admins group
    delete_permission = Permission.objects.get_or_create(
        codename='can_delete_book',
        content_type=content_type,
        defaults={'name': 'Can delete book'}
    )[0]
    admins_group.permissions.add(view_permission, create_permission, edit_permission, delete_permission)
    
    print("Groups and permissions setup completed!")
    print(f"Viewers group has {viewers_group.permissions.count()} permissions")
    print(f"Editors group has {editors_group.permissions.count()} permissions")
    print(f"Admins group has {admins_group.permissions.count()} permissions")

if __name__ == '__main__':
    setup_groups()
