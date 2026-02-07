#!/usr/bin/env python
"""Test script to verify new role creation"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from django.contrib.auth.models import Group
from core.models import Module, RolePermission

print("=" * 60)
print("اختبار إنشاء دور جديد")
print("=" * 60)

# Check before creation
print("\n📊 قبل الإنشاء:")
groups_before = Group.objects.count()
print(f"عدد الأدوار: {groups_before}")

# Create new role
test_role_name = "مدير المشاريع"
print(f"\n➕ جاري إنشاء دور جديد: {test_role_name}")

try:
    # Check if already exists
    if Group.objects.filter(name=test_role_name).exists():
        Group.objects.filter(name=test_role_name).delete()
        print(f"  تم حذف الدور القديم")
    
    # Create new group
    group = Group.objects.create(name=test_role_name)
    print(f"  ✅ تم إنشاء Group: {group.name} (ID: {group.id})")
    
    # Create default role permissions
    modules = Module.objects.all()
    perm_count = 0
    
    for module in modules:
        for action in ['view', 'add', 'change', 'delete', 'export']:
            RolePermission.objects.get_or_create(
                group=group,
                module=module,
                action=action,
                defaults={'is_allowed': True}
            )
            perm_count += 1
    
    print(f"  ✅ تم إنشاء {perm_count} صلاحية")
    
except Exception as e:
    print(f"  ❌ خطأ: {str(e)}")
    import traceback
    traceback.print_exc()

# Check after creation
print("\n📊 بعد الإنشاء:")
groups_after = Group.objects.count()
print(f"عدد الأدوار: {groups_after}")

# Verify the new role
print(f"\n✓ التحقق من دور '{test_role_name}':")
new_group = Group.objects.filter(name=test_role_name).first()
if new_group:
    perms = RolePermission.objects.filter(group=new_group)
    print(f"  ✅ الدور موجود (ID: {new_group.id})")
    print(f"  ✅ عدد الصلاحيات: {perms.count()}")
    
    # Show some sample permissions
    print(f"\n📋 عينة من الصلاحيات:")
    for perm in perms.filter(action='view'):
        print(f"    - {perm.module.name_ar}: {perm.action} = {perm.is_allowed}")
else:
    print(f"  ❌ الدور غير موجود!")

print("\n" + "=" * 60)
print("✅ الاختبار مكتمل")
print("=" * 60)
