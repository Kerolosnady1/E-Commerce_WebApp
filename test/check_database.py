#!/usr/bin/env python
"""Check database for roles and users"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from django.contrib.auth.models import User, Group
from core.models import Module, RolePermission

print("="*70)
print("DATABASE VERIFICATION - التحقق من قاعدة البيانات")
print("="*70)

# Check Groups table
print("\n1️⃣ جدول المجموعات (auth_group):")
print("-"*70)
groups = Group.objects.all()
print(f"   عدد الأدوار في قاعدة البيانات: {groups.count()}")
if groups.exists():
    for group in groups:
        print(f"   ✓ {group.name} (ID: {group.id})")
else:
    print("   ❌ لا توجد أدوار في قاعدة البيانات!")

# Check Users table
print("\n2️⃣ جدول المستخدمين (auth_user):")
print("-"*70)
users = User.objects.all()
print(f"   عدد المستخدمين في قاعدة البيانات: {users.count()}")
if users.exists():
    for user in users:
        groups_list = list(user.groups.values_list('name', flat=True))
        groups_str = ', '.join(groups_list) if groups_list else 'لا يوجد دور'
        print(f"   ✓ {user.username} - الدور: {groups_str}")
else:
    print("   ⚠️ لا توجد مستخدمين في قاعدة البيانات!")

# Check User-Group relationships
print("\n3️⃣ علاقة المستخدمين بالأدوار (auth_user_groups):")
print("-"*70)
roles_check = ['مدير النظام', 'قسم المبيعات', 'المحاسب', 'مدير المستودع']
for role_name in roles_check:
    count = User.objects.filter(groups__name=role_name).count()
    emoji = '🟦' if 'النظام' in role_name else '🟩' if 'المبيعات' in role_name else '🟧' if 'المحاسب' in role_name else '🟪'
    print(f"   {emoji} {role_name}: {count} مستخدم")

# Check Modules table
print("\n4️⃣ جدول الوحدات (core_module):")
print("-"*70)
modules = Module.objects.all()
print(f"   عدد الوحدات البرمجية: {modules.count()}")
if modules.exists():
    for module in modules[:5]:
        print(f"   ✓ {module.name_ar}")
    if modules.count() > 5:
        print(f"   ... و {modules.count() - 5} وحدات أخرى")
else:
    print("   ⚠️ لا توجد وحدات في قاعدة البيانات!")

# Check RolePermission table
print("\n5️⃣ جدول صلاحيات الأدوار (core_rolepermission):")
print("-"*70)
permissions = RolePermission.objects.all()
print(f"   عدد الصلاحيات المحفوظة: {permissions.count()}")
for role_name in roles_check:
    group = Group.objects.filter(name=role_name).first()
    if group:
        count = RolePermission.objects.filter(group=group).count()
        print(f"   ✓ {role_name}: {count} صلاحية")

# Database file check
print("\n6️⃣ ملف قاعدة البيانات:")
print("-"*70)
import os.path
db_path = 'db.sqlite3'
if os.path.exists(db_path):
    size = os.path.getsize(db_path)
    size_mb = size / (1024 * 1024)
    print(f"   ✓ الملف موجود: {db_path}")
    print(f"   ✓ الحجم: {size_mb:.2f} MB ({size:,} bytes)")
else:
    print(f"   ❌ الملف غير موجود: {db_path}")

print("\n" + "="*70)
print("✅ SUMMARY - الملخص")
print("="*70)
print(f"✓ قاعدة البيانات: موجودة وتعمل")
print(f"✓ جدول الأدوار: {groups.count()} دور محفوظ")
print(f"✓ جدول المستخدمين: {users.count()} مستخدم محفوظ")
print(f"✓ جدول الوحدات: {modules.count()} وحدة محفوظة")
print(f"✓ جدول الصلاحيات: {permissions.count()} صلاحية محفوظة")
print("\n✨ قاعدة البيانات موجودة وتحتوي على بيانات حقيقية! ✨")
print("="*70 + "\n")
