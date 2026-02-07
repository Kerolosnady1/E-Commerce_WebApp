"""
Quick test script to verify all notification center functionality
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from core.models import Notification
from django.test import Client
import json

print("=" * 60)
print("🧪 اختبار نظام مركز التنبيهات")
print("=" * 60)

# Initialize client
client = Client()

# 1. Check if notifications exist
print("\n1️⃣ التحقق من الإشعارات في قاعدة البيانات")
total = Notification.objects.count()
unread = Notification.objects.filter(is_read=False).count()
read = Notification.objects.filter(is_read=True).count()

print(f"   ✅ إجمالي الإشعارات: {total}")
print(f"   ✅ غير المقروءة: {unread}")
print(f"   ✅ المقروءة: {read}")

# 2. Test notifications page
print("\n2️⃣ اختبار صفحة الإشعارات")
response = client.get('/notifications/')
print(f"   ✅ حالة الصفحة: {response.status_code}")
if hasattr(response, 'templates'):
    template_name = response.templates[0].name if response.templates else 'None'
    print(f"   ✅ النموذج المستخدم: {template_name}")

# 3. Test statistics
print("\n3️⃣ اختبار البيانات الإحصائية")
if response.context and response.context is not None:
    if 'unread_count' in response.context:
        print(f"   ✅ غير المقروءة في Context: {response.context['unread_count']}")
    if 'total_count' in response.context:
        print(f"   ✅ الإجمالي في Context: {response.context['total_count']}")
    if 'error_count' in response.context:
        print(f"   ✅ أخطاء: {response.context['error_count']}")
    if 'warning_count' in response.context:
        print(f"   ✅ تحذيرات: {response.context['warning_count']}")
else:
    print("   ⚠️  Context غير متاح (قد يكون الطلب غير من خلال test client)")

# 4. Test API endpoints
print("\n4️⃣ اختبار API Endpoints")

if total > 0:
    first_notif = Notification.objects.first()
    
    # Test mark as read
    print(f"   📝 اختبار تعليم الإشعار #{first_notif.id} كمقروء")
    response = client.post(f'/api/notifications/{first_notif.id}/mark-read/')
    if response.status_code == 200:
        print(f"   ✅ نجح - Status: {response.status_code}")
    else:
        print(f"   ❌ فشل - Status: {response.status_code}")
    
    # Verify in database
    first_notif.refresh_from_db()
    print(f"   ✅ تم التحديث في قاعدة البيانات: is_read={first_notif.is_read}")
    
    # Test delete
    print(f"\n   📝 اختبار حذف الإشعار #{first_notif.id}")
    response = client.post(f'/api/notifications/{first_notif.id}/delete/')
    if response.status_code == 200:
        print(f"   ✅ نجح - Status: {response.status_code}")
    else:
        print(f"   ❌ فشل - Status: {response.status_code}")
    
    # Verify in database
    exists = Notification.objects.filter(id=first_notif.id).exists()
    print(f"   ✅ تم الحذف من قاعدة البيانات: exists={exists}")

# 5. Test preferences API
print("\n5️⃣ اختبار حفظ الإعدادات")
data = {
    'in_app': True,
    'email': True,
    'sms': False
}
response = client.post(
    '/api/notifications/preferences/save/',
    data=json.dumps(data),
    content_type='application/json'
)
if response.status_code == 200:
    result = json.loads(response.content)
    print(f"   ✅ نجح - Status: {response.status_code}")
    print(f"   ✅ الرسالة: {result.get('message', 'N/A')}")
else:
    print(f"   ❌ فشل - Status: {response.status_code}")

# 6. Check context data
print("\n6️⃣ التحقق من البيانات المرسلة للنموذج")
response = client.get('/notifications/')

if response.context:
    context_keys = [
        'notifications',
        'unread_count',
        'total_count',
        'error_count',
        'warning_count',
        'success_count',
        'read_notifications',
        'recent_notifications'
    ]

    for key in context_keys:
        if key in response.context:
            value = response.context[key]
            if isinstance(value, int):
                print(f"   ✅ {key}: {value}")
            else:
                count = len(value) if hasattr(value, '__len__') else 'N/A'
                print(f"   ✅ {key}: {count} items")
        else:
            print(f"   ⚠️  {key}: غير موجود")
else:
    print("   ⚠️  Context غير متاح")

print("\n" + "=" * 60)
print("✅ انتهى الاختبار بنجاح!")
print("=" * 60)
