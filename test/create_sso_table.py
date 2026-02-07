#!/usr/bin/env python
"""
Create SSO Configuration table directly using Django ORM
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from django.db import connection
from django.core.management import call_command

print("=" * 70)
print("🔧 إنشاء جدول SSO Configuration مباشرة")
print("=" * 70)

# محاولة 1: تطبيق جميع الـ migrations
print("\n1️⃣ تطبيق جميع الـ migrations...")
try:
    call_command('migrate', verbosity=2)
    print("   ✅ تم تطبيق الـ migrations")
except Exception as e:
    print(f"   ⚠️  خطأ: {e}")

# محاولة 2: فحص الجدول
print("\n2️⃣ فحص وجود الجدول...")
cursor = connection.cursor()
cursor.execute(
    "SELECT name FROM sqlite_master WHERE type='table' AND name='core_ssoconfiguration';"
)
result = cursor.fetchone()

if result:
    print(f"   ✅ جدول core_ssoconfiguration موجود!")
else:
    print(f"   ❌ جدول core_ssoconfiguration غير موجود")
    print(f"\n   📝 محاولة إنشاء الجدول يدويًا...")
    
    # إنشاء الجدول يدويًا
    sql = """
    CREATE TABLE core_ssoconfiguration (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        provider VARCHAR(20) NOT NULL UNIQUE,
        is_enabled BOOLEAN DEFAULT 0,
        google_client_id VARCHAR(255) DEFAULT '',
        google_client_secret VARCHAR(255) DEFAULT '',
        azure_tenant_id VARCHAR(255) DEFAULT '',
        azure_client_id VARCHAR(255) DEFAULT '',
        azure_client_secret VARCHAR(255) DEFAULT '',
        saml_entity_id VARCHAR(500) DEFAULT '',
        saml_sso_url VARCHAR(200) DEFAULT '',
        saml_certificate TEXT DEFAULT '',
        ldap_server_uri VARCHAR(500) DEFAULT '',
        ldap_bind_dn VARCHAR(500) DEFAULT '',
        ldap_bind_password VARCHAR(255) DEFAULT '',
        ldap_user_search_base VARCHAR(500) DEFAULT '',
        ldap_group_search_base VARCHAR(500) DEFAULT '',
        role_mapping JSON DEFAULT '{}',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_by_id INTEGER,
        FOREIGN KEY (updated_by_id) REFERENCES auth_user(id)
    );
    """
    
    try:
        cursor.execute(sql)
        connection.commit()
        print(f"   ✅ تم إنشاء الجدول بنجاح")
    except Exception as e:
        print(f"   ❌ خطأ: {e}")

# محاولة 3: فحص نهائي
print("\n3️⃣ فحص نهائي...")
cursor.execute(
    "SELECT name FROM sqlite_master WHERE type='table' AND name='core_ssoconfiguration';"
)
if cursor.fetchone():
    print(f"   ✅ جدول core_ssoconfiguration موجود الآن!")
else:
    print(f"   ❌ فشل إنشاء الجدول")

print("\n" + "=" * 70)
