#!/usr/bin/env python
"""اختبار ميزة حذف الدور"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from django.contrib.auth.models import Group, User
from core.models import RolePermission, Module
from django.test import Client
import json

print("=" * 70)
print("✅ اختبار ميزة حذف الدور")
print("=" * 70)

# إنشاء test user
user = User.objects.filter(username='testuser').first()
if not user:
    user = User.objects.create_user(username='testuser', password='testpass123')
    print("✓ تم إنشاء test user")
else:
    print("✓ استخدام test user الموجود")

client = Client()
client.login(username='testuser', password='testpass123')

# 1. اختبار محاولة حذف دور افتراضي
print("\n1️⃣ اختبار حذف دور افتراضي (يجب أن يفشل):")
response = client.post('/security/delete-role/', 
    json.dumps({'role_name': 'مدير النظام'}),
    content_type='application/json',
    HTTP_X_REQUESTED_WITH='XMLHttpRequest'
)
data = json.loads(response.content)
print(f"   Status: {response.status_code}")
print(f"   Success: {data.get('success')}")
print(f"   Message: {data.get('message')}")
if not data.get('success'):
    print(f"   ✅ الحماية تعمل بشكل صحيح!")

# 2. اختبار إنشاء دور مخصص وحذفه
print("\n2️⃣ اختبار حذف دور مخصص:")
test_role_name = "اختبار_حذف_" + str(__import__('time').time()).split('.')[0]

# إنشاء الدور
test_group = Group.objects.create(name=test_role_name)
print(f"   ✓ تم إنشاء دور: {test_role_name}")

# التحقق من وجوده
check = Group.objects.filter(name=test_role_name).first()
print(f"   ✓ الدور موجود: {check.name if check else 'لا'}")

# محاولة حذفه
response = client.post('/security/delete-role/',
    json.dumps({'role_name': test_role_name}),
    content_type='application/json',
    HTTP_X_REQUESTED_WITH='XMLHttpRequest'
)
data = json.loads(response.content)
print(f"   Status: {response.status_code}")
print(f"   Success: {data.get('success')}")
print(f"   Message: {data.get('message')}")

# التحقق من الحذف
check = Group.objects.filter(name=test_role_name).first()
if not check:
    print(f"   ✅ الدور تم حذفه بنجاح من Database!")
else:
    print(f"   ❌ الدور لا يزال موجود في Database!")

# 3. اختبار منع حذف دور به مستخدمين
print("\n3️⃣ اختبار منع حذف دور به مستخدمين:")
test_role_with_users = "دور_به_مستخدم_" + str(__import__('time').time()).split('.')[0]
group_with_users = Group.objects.create(name=test_role_with_users)
group_with_users.user_set.add(user)
print(f"   ✓ تم إنشاء دور: {test_role_with_users}")
print(f"   ✓ تم إضافة مستخدم للدور")

response = client.post('/security/delete-role/',
    json.dumps({'role_name': test_role_with_users}),
    content_type='application/json',
    HTTP_X_REQUESTED_WITH='XMLHttpRequest'
)
data = json.loads(response.content)
print(f"   Status: {response.status_code}")
print(f"   Success: {data.get('success')}")
print(f"   Message: {data.get('message')}")
if not data.get('success') and 'مستخدم' in data.get('message', ''):
    print(f"   ✅ الحماية تعمل بشكل صحيح!")

# Cleanup
group_with_users.user_set.remove(user)
group_with_users.delete()

print("\n" + "=" * 70)
print("✅ جميع الاختبارات مكتملة")
print("=" * 70)
