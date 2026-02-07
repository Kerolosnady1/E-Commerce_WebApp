#!/usr/bin/env python
"""
Display security logs from database
"""
import sqlite3
from datetime import datetime

db_path = 'db.sqlite3'

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n" + "=" * 90)
    print("🔐 سجلات الأمان - Security Logs")
    print("=" * 90)
    
    # التحقق من وجود الجدول
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='core_securitylog';"
    )
    if not cursor.fetchone():
        print("❌ جدول core_securitylog غير موجود!")
        exit(1)
    
    # عدد السجلات
    cursor.execute("SELECT COUNT(*) FROM core_securitylog;")
    total = cursor.fetchone()[0]
    
    print(f"\n📊 إجمالي سجلات الأمان: {total}\n")
    
    if total == 0:
        print("⚠️  لا توجد سجلات أمان حتى الآن")
        print("     (سيتم إنشاء سجلات عند تسجيل الدخول أو تغيير الإعدادات)")
    else:
        # عرض آخر 15 سجل
        cursor.execute("""
            SELECT 
                id, 
                username, 
                action_type, 
                description, 
                status, 
                ip_address,
                datetime(timestamp) as time
            FROM core_securitylog
            ORDER BY timestamp DESC
            LIMIT 15
        """)
        
        rows = cursor.fetchall()
        print("📋 آخر 15 سجل أمان:\n")
        
        for i, (log_id, username, action_type, description, status, ip_addr, timestamp) in enumerate(rows, 1):
            status_icon = "✅" if status == "success" else "⚠️" if status == "warning" else "❌"
            print(f"{i}. {status_icon} {action_type.upper()}")
            print(f"   👤 المستخدم: {username}")
            print(f"   📝 الوصف: {description}")
            print(f"   🌍 IP: {ip_addr or 'غير معروف'}")
            print(f"   ⏰ الوقت: {timestamp}\n")
    
    # إحصائيات
    if total > 0:
        print("-" * 90)
        print("\n📊 إحصائيات:\n")
        
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM core_securitylog
            GROUP BY status
            ORDER BY count DESC
        """)
        
        status_rows = cursor.fetchall()
        for status, count in status_rows:
            percentage = (count / total * 100)
            print(f"   {status}: {count} ({percentage:.1f}%)")
        
        print("\n🎯 أنواع الأحداث:\n")
        
        cursor.execute("""
            SELECT action_type, COUNT(*) as count
            FROM core_securitylog
            GROUP BY action_type
            ORDER BY count DESC
        """)
        
        action_rows = cursor.fetchall()
        for action, count in action_rows:
            percentage = (count / total * 100)
            print(f"   {action}: {count} ({percentage:.1f}%)")
    
    print("\n" + "=" * 90)
    
except Exception as e:
    print(f"❌ خطأ: {e}")
    import traceback
    traceback.print_exc()
