"""
Quick test script to verify the add_role functionality
Run: python manage.py shell < test_add_role.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from django.contrib.auth.models import Group, User
from django.test import Client
from core.models import Module, RolePermission

print("=" * 60)
print("Testing Add Role Functionality")
print("=" * 60)

# Get or create a test user
user, created = User.objects.get_or_create(
    username='testuser',
    defaults={'password': 'testpass123', 'is_staff': True}
)
print(f"\n✓ Test user: {user.username} ({'created' if created else 'exists'})")

# Create a test client
client = Client()
client.force_login(user)
print("✓ User logged in")

# Check if modules exist
modules = Module.objects.all()
print(f"✓ Modules in database: {modules.count()}")
if modules.count() == 0:
    print("  ⚠ Warning: No modules found. Populate them first!")

# Test 1: Add a new role
print("\n" + "=" * 60)
print("Test 1: Adding a new role")
print("=" * 60)

response = client.post('/security/add-role/', {
    'name': 'test_role_123',
    'description': 'Test role for testing',
    'require_2fa': 'on',
    'permission_level': 'standard'
})

print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")

if response.status_code == 200:
    data = response.json()
    if data.get('success'):
        print("✓ Role created successfully!")
        
        # Verify role exists
        try:
            group = Group.objects.get(name='test_role_123')
            print(f"✓ Group found in database: {group.name}")
            
            # Check RolePermissions
            perms = RolePermission.objects.filter(group=group)
            print(f"✓ RolePermissions created: {perms.count()}")
        except Group.DoesNotExist:
            print("✗ Group not found in database!")
    else:
        print(f"✗ Error: {data.get('message')}")
else:
    print(f"✗ HTTP Error: {response.status_code}")

# Test 2: Try to add duplicate role
print("\n" + "=" * 60)
print("Test 2: Adding duplicate role (should fail)")
print("=" * 60)

response = client.post('/security/add-role/', {
    'name': 'test_role_123',
    'description': 'Duplicate test',
    'require_2fa': 'off',
    'permission_level': 'standard'
})

data = response.json()
print(f"Response: {data}")

if not data.get('success'):
    print(f"✓ Correctly rejected duplicate: {data.get('message')}")
else:
    print("✗ Should have rejected duplicate!")

# Test 3: Try short name
print("\n" + "=" * 60)
print("Test 3: Adding role with short name (should fail)")
print("=" * 60)

response = client.post('/security/add-role/', {
    'name': 'ab',
    'description': 'Too short',
    'require_2fa': 'off',
    'permission_level': 'standard'
})

data = response.json()
print(f"Response: {data}")

if not data.get('success'):
    print(f"✓ Correctly rejected short name: {data.get('message')}")
else:
    print("✗ Should have rejected short name!")

# Test 4: Get role permissions
print("\n" + "=" * 60)
print("Test 4: Getting role permissions")
print("=" * 60)

response = client.get('/security/role-permissions/test_role_123/')
print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    if data.get('success'):
        print(f"✓ Retrieved permissions for: {data.get('role')}")
        modules = data.get('modules', [])
        print(f"  Modules: {len(modules)}")
        if modules:
            print(f"  First module: {modules[0].get('name_ar')}")
            print(f"  Permissions: {modules[0].get('permissions')}")
    else:
        print(f"✗ Error: {data.get('message')}")

# Cleanup
print("\n" + "=" * 60)
print("Cleanup")
print("=" * 60)

try:
    group = Group.objects.get(name='test_role_123')
    group.delete()
    print("✓ Test role deleted")
except Group.DoesNotExist:
    print("✓ Test role already deleted")

print("\n" + "=" * 60)
print("All tests completed!")
print("=" * 60)
