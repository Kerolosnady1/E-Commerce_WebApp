#!/usr/bin/env python
"""
Direct database check for security logs
"""
import sqlite3
from datetime import datetime, timedelta

db_path = 'db.sqlite3'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 80)
print("🔐 فحص سجلات الأمان من قاعدة البيانات")
print("=" * 80)

# 1️⃣ عدد السجلات الكلي
cursor.execute("SELECT COUNT(*) FROM core_securitylog;")
total = cursor.fetchone()[0]
print(f"\n📊 إجمالي سجلات الأمان: {total}")

# 2️⃣ آخر 10 سجلات
print(f"\n📋 آخر 10 سجلات أمان:")
print("-" * 80)

cursor.execute("""
    SELECT 
        id, username, action_type, description, status, ip_address, timestamp
    FROM core_securitylog
    ORDER BY timestamp DESC
    LIMIT 10
""")

rows = cursor.fetchall()
for i, row in enumerate(rows, 1):
    log_id, username, action_type, description, status, ip_addr, timestamp = row
    print(f"\n{i}️⃣ ID: {log_id}")
    print(f"   👤 المستخدم: {username}")
    print(f"   🎯 النوع: {action_type}")
    print(f"   📝 الوصف: {description}")
    print(f"   📊 الحالة: {status}")
    print(f"   🌍 IP: {ip_addr or 'غير معروف'}")
    print(f"   ⏰ الوقت: {timestamp}")

# 3️⃣ إحصائيات الأحداث
print("\n" + "-" * 80)
print("\n📊 إحصائيات الأحداث:")
print("-" * 80)

cursor.execute("""
    SELECT action_type, COUNT(*) as count
    FROM core_securitylog
    GROUP BY action_type
    ORDER BY count DESC
""")

action_rows = cursor.fetchall()
for action, count in action_rows:
    percentage = (count / total * 100) if total > 0 else 0
    print(f"   {action}: {count} ({percentage:.1f}%)")

# 4️⃣ إحصائيات الحالة
print("\n📊 إحصائيات الحالة:")
print("-" * 80)

cursor.execute("""
    SELECT status, COUNT(*) as count
    FROM core_securitylog
    GROUP BY status
    ORDER BY count DESC
""")

status_rows = cursor.fetchall()
for status, count in status_rows:
    percentage = (count / total * 100) if total > 0 else 0
    print(f"   {status}: {count} ({percentage:.1f}%)")

# 5️⃣ أكثر المستخدمين نشاطاً
print("\n👥 أكثر المستخدمين نشاطاً:")
print("-" * 80)

cursor.execute("""
    SELECT username, COUNT(*) as count
    FROM core_securitylog
    GROUP BY username
    ORDER BY count DESC
    LIMIT 5
""")

user_rows = cursor.fetchall()
for username, count in user_rows:
    print(f"   {username}: {count} حدث")

# 6️⃣ آخر أحداث SSO
print("\n🔐 آخر أحداث SSO:")
print("-" * 80)

cursor.execute("""
    SELECT username, description, status, timestamp
    FROM core_securitylog
    WHERE action_type = 'settings_change'
    ORDER BY timestamp DESC
    LIMIT 5
""")

sso_rows = cursor.fetchall()
if sso_rows:
    for username, description, status, timestamp in sso_rows:
        print(f"   • {username}: {description} ({status}) - {timestamp}")
else:
    print("   (لا توجد أحداث SSO حتى الآن)")

conn.close()
print("\n" + "=" * 80)
print("✅ اكتمل الفحص")
print("=" * 80)
