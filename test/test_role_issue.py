#!/usr/bin/env python
"""Test the role display issue"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from django.contrib.auth.models import Group
from core.models import Module, RolePermission
import json

print("=" * 60)
print("اختبار مشكلة الأدوار الجديدة")
print("=" * 60)

# Check existing roles
print("\n✓ الأدوار الموجودة:")
for group in Group.objects.all():
    perms = RolePermission.objects.filter(group=group).count()
    print(f"  - {group.name} (صلاحيات: {perms})")

# Test the endpoint
print("\n✓ اختبار الـ endpoint:")
from django.test import Client
client = Client()

test_role = "قسم المبيعات"
response = client.get(f'/security/role-permissions/{test_role}/')
print(f"  Status Code: {response.status_code}")

try:
    data = json.loads(response.content)
    print(f"  Success: {data.get('success')}")
    print(f"  Modules Count: {len(data.get('modules', []))}")
    if data.get('modules'):
        print(f"  First Module: {data['modules'][0].get('name_ar')}")
except:
    print(f"  Response: {response.content[:100]}")

print("\n" + "=" * 60)
