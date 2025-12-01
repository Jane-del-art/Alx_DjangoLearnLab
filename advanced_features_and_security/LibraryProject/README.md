# Permissions and Groups Setup

## Overview
This Django application implements a role-based access control system using Django's built-in permissions and groups.

## Custom Permissions
The Book model has four custom permissions:
1. `can_view_book` - Allows viewing books
2. `can_create_book` - Allows creating new books
3. `can_edit_book` - Allows editing existing books
4. `can_delete_book` - Allows deleting books

## Groups
Three default groups are created:

### 1. Viewers
- Permission: `can_view_book`
- Can only view books in the list

### 2. Editors
- Permissions: `can_view_book`, `can_create_book`, `can_edit_book`
- Can view, create, and edit books
- Cannot delete books

### 3. Admins
- All permissions: `can_view_book`, `can_create_book`, `can_edit_book`, `can_delete_book`
- Full access to all book operations

## How to Use

### 1. Setup Groups and Permissions
Run the setup script:
```bash
python manage.py shell < setup_permissions.py
