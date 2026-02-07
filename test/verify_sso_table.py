#!/usr/bin/env python
"""
Verify and fix SSO Configuration table
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from django.db import connection
from django.db.migrations.executor import MigrationExecutor

print("=" * 70)
print("🔍 فحص حالة قاعدة البيانات")
print("=" * 70)

# التحقق من الجداول
cursor = connection.cursor()

print("\n1️⃣ فحص وجود جدول core_ssoconfiguration...")
cursor.execute(
    "SELECT name FROM sqlite_master WHERE type='table' AND name='core_ssoconfiguration'"
)
table_exists = cursor.fetchone() is not None
print(f"   {'✅ موجود' if table_exists else '❌ غير موجود'}")

# التحقق من الـ migrations المطبقة
print("\n2️⃣ فحص الـ migrations المطبقة...")
executor = MigrationExecutor(connection)
plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
print(f"   📊 عدد الـ migrations المتبقية: {len(plan)}")

# عرض آخر 5 migrations
applied = executor.recorder.applied_migrations()
recent = sorted(list(applied))[-5:]
print(f"   📊 آخر 5 migrations مطبقة:")
for migration in recent:
    app, name = migration
    print(f"      - {app}: {name}")

if not table_exists:
    print("\n⚠️  جدول core_ssoconfiguration غير موجود!")
    print("📝 تطبيق الـ migration الآن...")
    
    try:
        from django.core.management import call_command
        call_command('migrate', 'core')
        print("✅ تم تطبيق migrations")
        
        # التحقق مرة أخرى
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='core_ssoconfiguration'"
        )
        if cursor.fetchone():
            print("✅ جدول core_ssoconfiguration تم إنشاؤه بنجاح!")
        else:
            print("❌ فشل إنشاء الجدول")
    except Exception as e:
        print(f"❌ خطأ: {e}")
else:
    print("\n✅ جدول core_ssoconfiguration موجود!")
    
    # عرض معلومات الجدول
    cursor.execute("PRAGMA table_info(core_ssoconfiguration)")
    columns = cursor.fetchall()
    print(f"\n📋 أعمدة الجدول ({len(columns)} عمود):")
    for col in columns:
        print(f"   - {col[1]} ({col[2]})")

print("\n" + "=" * 70)
