#!/usr/bin/env python
"""
اختبار شامل لوظيفة حفظ SSO
Testing the SSO save functionality
"""

import os
import django
import json
from django.test import Client
from django.contrib.auth.models import User

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

print("=" * 60)
print("🔍 اختبار وظيفة حفظ SSO - SSO Save Functionality Test")
print("=" * 60)

# ✅ الخطوة 1: التحقق من نموذج SSOConfiguration
print("\n1️⃣ التحقق من نموذج SSOConfiguration...")
try:
    from core.models import SSOConfiguration
    print("   ✅ نموذج SSOConfiguration موجود")
    print(f"   📊 عدد الإعدادات الموجودة: {SSOConfiguration.objects.count()}")
except Exception as e:
    print(f"   ❌ خطأ: {e}")
    exit(1)

# ✅ الخطوة 2: التحقق من وجود مستخدم للاختبار
print("\n2️⃣ التحقق من وجود مستخدم اختبار...")
try:
    test_user = User.objects.filter(username='testuser').first()
    if not test_user:
        test_user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@test.com'
        )
        print(f"   ✅ تم إنشاء مستخدم اختبار: {test_user.username}")
    else:
        print(f"   ✅ مستخدم اختبار موجود: {test_user.username}")
except Exception as e:
    print(f"   ❌ خطأ: {e}")
    exit(1)

# ✅ الخطوة 3: اختبار API بدون تسجيل دخول
print("\n3️⃣ اختبار API بدون تسجيل دخول (يجب أن يفشل)...")
client = Client()
test_data = {
    'google': {
        'is_enabled': True,
        'client_id': 'test_google_id',
        'client_secret': 'test_google_secret',
    },
    'azure': {
        'is_enabled': False,
        'tenant_id': '',
        'client_id': '',
        'client_secret': '',
    },
    'saml2': {
        'is_enabled': False,
        'entity_id': '',
        'sso_url': '',
        'certificate': '',
    },
    'ldap': {
        'is_enabled': False,
        'server_uri': '',
        'bind_dn': '',
        'bind_password': '',
        'user_search_base': '',
    }
}

try:
    response = client.post(
        '/api/sso/save/',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    print(f"   📡 HTTP Status (بدون تسجيل دخول): {response.status_code}")
    if response.status_code == 403:
        print("   ✅ يتم الرفض بشكل صحيح (403 - يجب تسجيل الدخول)")
    else:
        print(f"   ⚠️ Response: {response.json()}")
except Exception as e:
    print(f"   ❌ خطأ: {e}")

# ✅ الخطوة 4: اختبار API مع تسجيل دخول
print("\n4️⃣ اختبار API مع تسجيل دخول (يجب أن ينجح)...")
try:
    # تسجيل الدخول
    login_success = client.login(username='testuser', password='testpass123')
    if login_success:
        print("   ✅ تم تسجيل الدخول بنجاح")
    else:
        print("   ❌ فشل تسجيل الدخول")
        exit(1)
    
    # محاولة الحفظ
    response = client.post(
        '/api/sso/save/',
        data=json.dumps(test_data),
        content_type='application/json',
        HTTP_X_CSRFTOKEN=client.cookies.get('csrftoken', '').value or 'test'
    )
    
    print(f"   📡 HTTP Status (مع تسجيل دخول): {response.status_code}")
    result = response.json()
    print(f"   📋 Response: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    if result.get('success'):
        print("   ✅ تم الحفظ بنجاح!")
    else:
        print(f"   ❌ فشل الحفظ: {result.get('error')}")
        
except Exception as e:
    print(f"   ❌ خطأ: {e}")
    import traceback
    traceback.print_exc()

# ✅ الخطوة 5: التحقق من البيانات المحفوظة
print("\n5️⃣ التحقق من البيانات المحفوظة...")
try:
    google_config = SSOConfiguration.objects.get(provider='google')
    print(f"   ✅ إعدادات Google:")
    print(f"      - مفعل: {google_config.is_enabled}")
    print(f"      - Client ID: {google_config.google_client_id}")
    print(f"      - Client Secret: {google_config.google_client_secret[:20]}..." if google_config.google_client_secret else "      - Client Secret: (فارغ)")
    
except SSOConfiguration.DoesNotExist:
    print("   ❌ لم يتم حفظ إعدادات Google")

# ✅ الخطوة 6: اختبار تحميل البيانات
print("\n6️⃣ اختبار تحميل البيانات (GET)...")
try:
    response = client.get('/api/sso/load/')
    print(f"   📡 HTTP Status: {response.status_code}")
    result = response.json()
    if result.get('success'):
        print("   ✅ تم تحميل البيانات بنجاح")
        print(f"   📋 عدد المزودين: {len(result.get('configs', []))}")
    else:
        print(f"   ❌ فشل التحميل: {result.get('error')}")
except Exception as e:
    print(f"   ❌ خطأ: {e}")

print("\n" + "=" * 60)
print("✅ انتهى الاختبار")
print("=" * 60)
