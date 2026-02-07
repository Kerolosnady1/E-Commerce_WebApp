#!/usr/bin/env python
"""
Quick check of SSO table
"""
import sqlite3

db_path = 'db.sqlite3'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 70)
print("🔍 فحص جدول SSO في قاعدة البيانات")
print("=" * 70)

# 1. عرض جميع الجداول
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = cursor.fetchall()

print(f"\n📊 عدد الجداول: {len(tables)}")
print("📋 البحث عن جداول SSO...")

sso_table_exists = False
for table in tables:
    if 'sso' in table[0].lower():
        print(f"   ✅ {table[0]}")
        sso_table_exists = True

if not sso_table_exists:
    print("   ❌ لا توجد جداول SSO")
else:
    print("\n✅ جدول SSO موجود!")
    
    # 2. عرض أعمدة الجدول
    cursor.execute("PRAGMA table_info(core_ssoconfiguration);")
    columns = cursor.fetchall()
    print(f"\n📋 أعمدة الجدول:")
    for col in columns:
        print(f"   - {col[1]} ({col[2]})")
    
    # 3. عرض عدد السجلات
    cursor.execute("SELECT COUNT(*) FROM core_ssoconfiguration;")
    count = cursor.fetchone()[0]
    print(f"\n📊 عدد السجلات: {count}")
    
    if count == 0:
        print("   (الجدول فارغ - سيتم ملؤه عند الحفظ)")

conn.close()
print("\n" + "=" * 70)
