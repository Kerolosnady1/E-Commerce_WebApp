#!/usr/bin/env python
"""تشخيص مشكلة الأدوار الجديدة - نسخة محسّنة"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from django.contrib.auth.models import Group, User
from core.models import Module, RolePermission
from django.test import Client
import json

print("=" * 70)
print("🔍 تشخيص شامل لمشكلة الأدوار الجديدة")
print("=" * 70)

# 1. التحقق من الأدوار
print("\n1️⃣ الأدوار الموجودة في Database:")
groups = Group.objects.all()
for group in groups:
    perms = RolePermission.objects.filter(group=group).count()
    users = group.user_set.count()
    print(f"   - {group.name} (ID: {group.id}, صلاحيات: {perms}, مستخدمون: {users})")

# 2. التحقق من الوحدات
print("\n2️⃣ الوحدات (Modules):")
modules = Module.objects.all()
print(f"   عدد الوحدات: {modules.count()}")
for module in modules:
    print(f"   - {module.name_ar} ({module.name_en})")

# 3. اختبار الـ Endpoint بدون authentication
print("\n3️⃣ اختبار /security/role-permissions/ بدون authentication:")
client = Client()
response = client.get('/security/role-permissions/قسم المبيعات/')
print(f"   Status: {response.status_code}")
if response.status_code == 302:
    print(f"   ⚠️ يعيد 302 redirect! (يحتاج login)")
    print(f"   Redirect to: {response.get('Location', 'N/A')}")
elif response.status_code == 200:
    data = json.loads(response.content)
    print(f"   ✅ نجح! Success: {data.get('success')}")
else:
    print(f"   ❌ خطأ: {response.status_code}")

# 4. اختبار مع user مصرح
print("\n4️⃣ اختبار /security/role-permissions/ مع authenticated user:")
# إنشاء test user إذا لم يكن موجود
user = User.objects.filter(username='testuser').first()
if not user:
    user = User.objects.create_user(username='testuser', password='testpass123')
    print(f"   ✓ تم إنشاء test user: testuser")
else:
    print(f"   ✓ استخدام user موجود: testuser")

# Login
client.login(username='testuser', password='testpass123')
response = client.get('/security/role-permissions/قسم المبيعات/')
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    try:
        data = json.loads(response.content)
        print(f"   ✅ نجح!")
        print(f"   Success: {data.get('success')}")
        print(f"   Role: {data.get('role')}")
        print(f"   Modules count: {len(data.get('modules', []))}")
        if data.get('modules'):
            first = data['modules'][0]
            print(f"   First module: {first.get('name_ar')}")
            print(f"   Permissions: {first.get('permissions')}")
    except Exception as e:
        print(f"   ❌ خطأ في parsing JSON: {str(e)}")
        print(f"   Response: {response.content[:200]}")
else:
    print(f"   ❌ خطأ: {response.status_code}")

# 5. اختبار إضافة دور جديد
print("\n5️⃣ اختبار إضافة دور جديد:")
test_role_name = "test_role_" + str(__import__('time').time()).split('.')[0]
response = client.post('/security/add-role/', {
    'name': test_role_name,
    'description': 'دور اختبار',
    'require_2fa': 'off',
    'permission_level': 'standard'
}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

print(f"   Status: {response.status_code}")
try:
    data = json.loads(response.content)
    print(f"   Success: {data.get('success')}")
    if data.get('success'):
        print(f"   ✅ تم إنشاء الدور: {data.get('group_name')}")
        
        # التحقق من أنه في database
        check = Group.objects.filter(name=test_role_name).first()
        if check:
            print(f"   ✅ الدور موجود في Database (ID: {check.id})")
            perms = RolePermission.objects.filter(group=check).count()
            print(f"   ✅ له {perms} صلاحية")
        else:
            print(f"   ❌ الدور غير موجود في Database!")
    else:
        print(f"   ❌ خطأ: {data.get('message')}")
except Exception as e:
    print(f"   ❌ خطأ في parsing: {str(e)}")

# 6. تجربة الـ endpoint مع الدور الجديد
if test_role_name and Group.objects.filter(name=test_role_name).exists():
    print(f"\n6️⃣ اختبار /security/role-permissions/ مع الدور الجديد:")
    response = client.get(f'/security/role-permissions/{test_role_name}/')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        try:
            data = json.loads(response.content)
            print(f"   ✅ نجح!")
            print(f"   Success: {data.get('success')}")
            print(f"   Modules count: {len(data.get('modules', []))}")
        except:
            print(f"   ❌ خطأ في parsing")
    else:
        print(f"   ❌ خطأ: {response.status_code}")

print("\n" + "=" * 70)
print("✅ التشخيص مكتمل")
print("=" * 70)
