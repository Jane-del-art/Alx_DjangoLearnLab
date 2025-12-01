# LibraryProject/bookshelf/management/commands/setup_groups.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from bookshelf.models import Book

class Command(BaseCommand):
    help = 'Creates default groups and assigns permissions'

    def handle(self, *args, **kwargs):
        # Get content type for Book model
        content_type = ContentType.objects.get_for_model(Book)
        
        # Get all permissions for Book model
        book_permissions = Permission.objects.filter(content_type=content_type)
        
        # Create groups
        viewers_group, created = Group.objects.get_or_create(name='Viewers')
        editors_group, created = Group.objects.get_or_create(name='Editors')
        admins_group, created = Group.objects.get_or_create(name='Admins')
        
        # Assign permissions to Viewers group
        view_permission = Permission.objects.get(codename='can_view_book')
        viewers_group.permissions.add(view_permission)
        
        # Assign permissions to Editors group
        create_permission = Permission.objects.get(codename='can_create_book')
        edit_permission = Permission.objects.get(codename='can_edit_book')
        editors_group.permissions.add(view_permission, create_permission, edit_permission)
        
        # Assign all permissions to Admins group
        for perm in book_permissions:
            admins_group.permissions.add(perm)
        
        self.stdout.write(self.style.SUCCESS('Successfully created groups and assigned permissions'))