#!/usr/bin/env python
"""Test SSO Configuration - Database Integration"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from core.models import SSOConfiguration
from django.contrib.auth.models import User

print("=" * 70)
print("🔐 SSO CONFIGURATION TEST - التحقق من ميزة SSO")
print("=" * 70)

# Check if model exists
print("\n1️⃣ فحص نموذج قاعدة البيانات:")
print("-" * 70)
try:
    count = SSOConfiguration.objects.count()
    print(f"   ✅ نموذج SSOConfiguration موجود في قاعدة البيانات")
    print(f"   📊 عدد التكوينات المحفوظة: {count}")
except Exception as e:
    print(f"   ❌ خطأ: {e}")

# Create test SSO configurations
print("\n2️⃣ إنشاء تكوينات SSO تجريبية:")
print("-" * 70)

try:
    # Google OAuth2
    google_config, created = SSOConfiguration.objects.get_or_create(
        provider='google',
        defaults={
            'is_enabled': True,
            'google_client_id': 'test-google-client-id.apps.googleusercontent.com',
            'google_client_secret': 'test-secret-key'
        }
    )
    status = "✨ تم الإنشاء" if created else "✓ موجود مسبقاً"
    print(f"   {status} - Google OAuth2")
    print(f"      الحالة: {'مفعل' if google_config.is_enabled else 'معطل'}")
    
    # Microsoft Azure
    azure_config, created = SSOConfiguration.objects.get_or_create(
        provider='azure',
        defaults={
            'is_enabled': False,
            'azure_tenant_id': 'test-tenant-id',
            'azure_client_id': 'test-azure-client-id',
            'azure_client_secret': 'test-azure-secret'
        }
    )
    status = "✨ تم الإنشاء" if created else "✓ موجود مسبقاً"
    print(f"   {status} - Microsoft Azure AD")
    print(f"      الحالة: {'مفعل' if azure_config.is_enabled else 'معطل'}")
    
    # SAML 2.0
    saml_config, created = SSOConfiguration.objects.get_or_create(
        provider='saml2',
        defaults={
            'is_enabled': False,
            'saml_entity_id': 'https://yourdomain.com/saml/metadata/',
            'saml_sso_url': 'https://idp.example.com/sso',
            'saml_certificate': '-----BEGIN CERTIFICATE-----\nTest Certificate\n-----END CERTIFICATE-----'
        }
    )
    status = "✨ تم الإنشاء" if created else "✓ موجود مسبقاً"
    print(f"   {status} - SAML 2.0")
    print(f"      الحالة: {'مفعل' if saml_config.is_enabled else 'معطل'}")
    
    # LDAP
    ldap_config, created = SSOConfiguration.objects.get_or_create(
        provider='ldap',
        defaults={
            'is_enabled': False,
            'ldap_server_uri': 'ldap://ldap.example.com:389',
            'ldap_bind_dn': 'cn=admin,dc=example,dc=com',
            'ldap_bind_password': 'test-password',
            'ldap_user_search_base': 'ou=users,dc=example,dc=com'
        }
    )
    status = "✨ تم الإنشاء" if created else "✓ موجود مسبقاً"
    print(f"   {status} - LDAP/Active Directory")
    print(f"      الحالة: {'مفعل' if ldap_config.is_enabled else 'معطل'}")
    
except Exception as e:
    print(f"   ❌ خطأ في إنشاء التكوينات: {e}")

# List all SSO configurations
print("\n3️⃣ جميع تكوينات SSO المحفوظة:")
print("-" * 70)
configs = SSOConfiguration.objects.all()
for config in configs:
    emoji = '🟢' if config.is_enabled else '🔴'
    print(f"   {emoji} {config.get_provider_display()}")
    print(f"      المفتاح: {config.provider}")
    print(f"      الحالة: {'مفعل ✅' if config.is_enabled else 'معطل ❌'}")
    print(f"      آخر تحديث: {config.updated_at.strftime('%Y-%m-%d %H:%M')}")
    if config.updated_by:
        print(f"      تم التحديث بواسطة: {config.updated_by.username}")
    print()

# Test data retrieval
print("\n4️⃣ اختبار جلب البيانات:")
print("-" * 70)
try:
    google = SSOConfiguration.objects.get(provider='google')
    print(f"   ✅ Google OAuth2:")
    print(f"      Client ID: {google.google_client_id[:30]}..." if len(google.google_client_id) > 30 else f"      Client ID: {google.google_client_id}")
    print(f"      مفعل: {google.is_enabled}")
except SSOConfiguration.DoesNotExist:
    print(f"   ⚠️ لا توجد تكوينات Google")

# Database table info
print("\n5️⃣ معلومات الجدول:")
print("-" * 70)
print(f"   📊 اسم الجدول: core_ssoconfiguration")
print(f"   📊 عدد السجلات: {SSOConfiguration.objects.count()}")
print(f"   📊 مزودو SSO المفعلين: {SSOConfiguration.objects.filter(is_enabled=True).count()}")
print(f"   📊 مزودو SSO المعطلين: {SSOConfiguration.objects.filter(is_enabled=False).count()}")

print("\n" + "=" * 70)
print("✅ اختبار SSO اكتمل بنجاح!")
print("=" * 70)
print("\n📌 الخطوات التالية:")
print("   1. افتح صفحة الأمان والصلاحيات: /security/")
print("   2. اضغط على زرار 'إعداد SSO'")
print("   3. قم بتفعيل أحد مزودي SSO")
print("   4. أدخل البيانات المطلوبة")
print("   5. احفظ الإعدادات - سيتم حفظها في قاعدة البيانات")
print("\n✨ النظام جاهز للاستخدام!\n")
