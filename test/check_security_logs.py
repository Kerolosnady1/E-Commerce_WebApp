#!/usr/bin/env python
"""
Check Security Logs - Dynamic and Real
تحقق من سجلات الأمان - ديناميكية وحقيقية
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from core.models import SecurityLog
from django.utils import timezone
from datetime import timedelta

print("=" * 80)
print("🔐 فحص سجلات الأمان - Security Logs Audit")
print("=" * 80)

# 1️⃣ عدد السجلات الكلي
total_logs = SecurityLog.objects.count()
print(f"\n📊 إجمالي سجلات الأمان: {total_logs}")

# 2️⃣ آخر 10 سجلات
print(f"\n📋 آخر 10 سجلات أمان:")
print("-" * 80)

logs = SecurityLog.objects.all().order_by('-timestamp')[:10]

for i, log in enumerate(logs, 1):
    action_display = log.get_action_type_display()
    time_diff = timezone.now() - log.timestamp
    
    # تحديد كم المدة منذ الحدث
    if time_diff.total_seconds() < 60:
        time_str = "قبل لحظات"
    elif time_diff.total_seconds() < 3600:
        minutes = int(time_diff.total_seconds() / 60)
        time_str = f"قبل {minutes} دقيقة" if minutes == 1 else f"قبل {minutes} دقائق"
    elif time_diff.total_seconds() < 86400:
        hours = int(time_diff.total_seconds() / 3600)
        time_str = f"قبل {hours} ساعة" if hours == 1 else f"قبل {hours} ساعات"
    else:
        days = int(time_diff.total_seconds() / 86400)
        time_str = f"قبل {days} يوم" if days == 1 else f"قبل {days} أيام"
    
    print(f"\n{i}️⃣ {action_display}")
    print(f"   👤 المستخدم: {log.username}")
    print(f"   📝 الوصف: {log.description}")
    print(f"   📊 الحالة: {log.get_status_display()}")
    print(f"   🌍 IP: {log.ip_address or 'غير معروف'}")
    print(f"   ⏰ الوقت: {log.timestamp.strftime('%Y-%m-%d %H:%M:%S')} ({time_str})")

# 3️⃣ إحصائيات الأحداث
print("\n" + "-" * 80)
print("\n📊 إحصائيات الأحداث:")
print("-" * 80)

action_stats = {}
for log in SecurityLog.objects.all():
    action = log.get_action_type_display()
    action_stats[action] = action_stats.get(action, 0) + 1

for action, count in sorted(action_stats.items(), key=lambda x: x[1], reverse=True):
    percentage = (count / total_logs * 100) if total_logs > 0 else 0
    print(f"   {action}: {count} ({percentage:.1f}%)")

# 4️⃣ إحصائيات الحالة
print("\n📊 إحصائيات الحالة:")
print("-" * 80)

status_stats = {}
for log in SecurityLog.objects.all():
    status = log.get_status_display()
    status_stats[status] = status_stats.get(status, 0) + 1

for status, count in sorted(status_stats.items(), key=lambda x: x[1], reverse=True):
    percentage = (count / total_logs * 100) if total_logs > 0 else 0
    print(f"   {status}: {count} ({percentage:.1f}%)")

# 5️⃣ آخر الأنشطة في آخر 24 ساعة
print("\n🔄 الأنشطة في آخر 24 ساعة:")
print("-" * 80)

last_24h = timezone.now() - timedelta(hours=24)
recent_logs = SecurityLog.objects.filter(timestamp__gte=last_24h)
print(f"   📊 عدد السجلات: {recent_logs.count()}")

if recent_logs.count() > 0:
    print(f"   ✅ هناك أنشطة حقيقية!")
else:
    print(f"   ⚠️  لا توجد أنشطة في آخر 24 ساعة")

# 6️⃣ أكثر المستخدمين نشاطاً
print("\n👥 أكثر المستخدمين نشاطاً:")
print("-" * 80)

user_stats = {}
for log in SecurityLog.objects.all():
    user = log.username or 'مجهول'
    user_stats[user] = user_stats.get(user, 0) + 1

for user, count in sorted(user_stats.items(), key=lambda x: x[1], reverse=True)[:5]:
    print(f"   {user}: {count} حدث")

print("\n" + "=" * 80)
print("✅ اكتمل الفحص")
print("=" * 80)
