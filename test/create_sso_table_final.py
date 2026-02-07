#!/usr/bin/env python
"""
Create SSO Configuration table directly in SQLite
"""
import sqlite3
import os

db_path = 'db.sqlite3'

if not os.path.exists(db_path):
    print(f"❌ ملف قاعدة البيانات غير موجود: {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 70)
print("🔧 إنشاء جدول SSO Configuration")
print("=" * 70)

# إنشاء الجدول
sql = """
CREATE TABLE IF NOT EXISTS core_ssoconfiguration (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider VARCHAR(20) NOT NULL UNIQUE,
    is_enabled BOOLEAN NOT NULL DEFAULT 0,
    google_client_id VARCHAR(255) NOT NULL DEFAULT '',
    google_client_secret VARCHAR(255) NOT NULL DEFAULT '',
    azure_tenant_id VARCHAR(255) NOT NULL DEFAULT '',
    azure_client_id VARCHAR(255) NOT NULL DEFAULT '',
    azure_client_secret VARCHAR(255) NOT NULL DEFAULT '',
    saml_entity_id VARCHAR(500) NOT NULL DEFAULT '',
    saml_sso_url VARCHAR(200) NOT NULL DEFAULT '',
    saml_certificate TEXT NOT NULL DEFAULT '',
    ldap_server_uri VARCHAR(500) NOT NULL DEFAULT '',
    ldap_bind_dn VARCHAR(500) NOT NULL DEFAULT '',
    ldap_bind_password VARCHAR(255) NOT NULL DEFAULT '',
    ldap_user_search_base VARCHAR(500) NOT NULL DEFAULT '',
    ldap_group_search_base VARCHAR(500) NOT NULL DEFAULT '',
    role_mapping TEXT NOT NULL DEFAULT '{}',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by_id INTEGER
)
"""

try:
    cursor.execute(sql)
    conn.commit()
    print("✅ تم إنشاء الجدول core_ssoconfiguration")
except sqlite3.OperationalError as e:
    if "already exists" in str(e):
        print("✅ الجدول موجود بالفعل")
    else:
        print(f"❌ خطأ: {e}")
        conn.close()
        exit(1)

# التحقق من وجود الجدول
cursor.execute(
    "SELECT name FROM sqlite_master WHERE type='table' AND name='core_ssoconfiguration';"
)
if cursor.fetchone():
    print("✅ تم التحقق: الجدول موجود الآن!")
    
    # عرض معلومات الجدول
    cursor.execute("PRAGMA table_info(core_ssoconfiguration);")
    columns = cursor.fetchall()
    print(f"\n📋 عدد الأعمدة: {len(columns)}")
    
    # عرض عدد السجلات
    cursor.execute("SELECT COUNT(*) FROM core_ssoconfiguration;")
    count = cursor.fetchone()[0]
    print(f"📊 عدد السجلات: {count}")
else:
    print("❌ فشل إنشاء الجدول")
    exit(1)

conn.close()
print("\n" + "=" * 70)
print("✅ انتهى!")
