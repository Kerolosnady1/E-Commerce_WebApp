#!/usr/bin/env python
"""
Direct database check and migration application
"""

import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from django.db import connection
from django.core.management import call_command
from django.db.migrations.executor import MigrationExecutor

print("=" * 70)
print("🔧 فحص وإصلاح قاعدة البيانات - Database Check & Fix")
print("=" * 70)

# 1️⃣ فحص قاعدة البيانات الحالية
print("\n1️⃣ فحص حالة قاعدة البيانات...")

cursor = connection.cursor()

# قائمة بجميع الجداول
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = cursor.fetchall()

print(f"   📊 عدد الجداول: {len(tables)}")
print(f"   📋 الجداول الموجودة:")
for table in tables:
    print(f"      - {table[0]}")

# البحث عن جدول SSO
sso_table_exists = any('ssoconfiguration' in table[0].lower() for table in tables)
print(f"\n   {'✅ جدول SSO موجود' if sso_table_exists else '❌ جدول SSO غير موجود'}")

# 2️⃣ فحص الـ migrations
print("\n2️⃣ فحص حالة الـ migrations...")

executor = MigrationExecutor(connection)
applied = executor.recorder.applied_migrations()
applied_list = sorted(list(applied))

print(f"   📊 عدد الـ migrations المطبقة: {len(applied_list)}")
print(f"   📋 آخر 5 migrations:")

for migration in applied_list[-5:]:
    app, name = migration
    print(f"      - {app}: {name}")

# التحقق من 0015_ssoconfiguration
sso_migration_applied = any('ssoconfiguration' in name.lower() for app, name in applied_list)
print(f"\n   {'✅ migration SSO مطبق' if sso_migration_applied else '❌ migration SSO غير مطبق'}")

# 3️⃣ تطبيق الـ migrations المتبقية
if not sso_migration_applied:
    print("\n3️⃣ تطبيق الـ migrations المتبقية...")
    try:
        # محاولة تطبيق جميع الـ migrations
        call_command('migrate', 'core', verbosity=2)
        print("   ✅ تم تطبيق الـ migrations بنجاح")
    except Exception as e:
        print(f"   ❌ خطأ عند تطبيق الـ migrations: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

# 4️⃣ فحص نهائي
print("\n4️⃣ فحص نهائي...")

cursor = connection.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%ssoconfiguration%';")
result = cursor.fetchone()

if result:
    print(f"   ✅ جدول core_ssoconfiguration موجود الآن!")
    
    # عرض معلومات الجدول
    cursor.execute("PRAGMA table_info(core_ssoconfiguration);")
    columns = cursor.fetchall()
    print(f"\n   📋 أعمدة الجدول ({len(columns)} عمود):")
    for col in columns:
        col_id, col_name, col_type, col_notnull, col_default, col_pk = col
        print(f"      - {col_name} ({col_type})")
else:
    print(f"   ❌ جدول core_ssoconfiguration لا يزال غير موجود!")
    sys.exit(1)

print("\n" + "=" * 70)
print("✅ انتهى الفحص والإصلاح")
print("=" * 70)
