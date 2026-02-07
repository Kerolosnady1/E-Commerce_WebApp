#!/usr/bin/env python
"""Test script to verify role data"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from django.contrib.auth.models import Group
from core.models import Module, RolePermission

print("=" * 50)
print("ROLE DATA TEST")
print("=" * 50)

# Check all groups
print("\n✓ All Groups:")
for group in Group.objects.all():
    print(f"  - {group.name} (ID: {group.id})")

# Check all modules
print("\n✓ All Modules:")
for module in Module.objects.all():
    print(f"  - {module.name_ar} ({module.name_en})")

# Check role permissions
print("\n✓ Role Permissions Count:")
total_perms = RolePermission.objects.count()
print(f"  Total: {total_perms}")

# Check if a specific role has permissions
test_role = "قسم المبيعات"
print(f"\n✓ Permissions for '{test_role}':")
group = Group.objects.filter(name=test_role).first()
if group:
    perms = RolePermission.objects.filter(group=group)
    print(f"  Found {perms.count()} permissions")
    for perm in perms:
        print(f"    - {perm.module.name_ar}: {perm.action} = {perm.is_allowed}")
else:
    print(f"  Group '{test_role}' not found!")

print("\n" + "=" * 50)
