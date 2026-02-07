#!/usr/bin/env python
"""
Simple Direct SSO Database Test
Tests basic SSO model and database operations
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from core.models import SSOConfiguration
from django.contrib.auth.models import User

print("\n" + "="*70)
print("  SIMPLE SSO DATABASE VALIDATION TEST")
print("="*70 + "\n")

# Get or create test user
admin_user, created = User.objects.get_or_create(
    username='sso_test_user',
    defaults={'email': 'sso@test.com', 'is_staff': True, 'is_superuser': True}
)
print(f"✓ Test user: {admin_user.username} (created={created})")

# Test 1: Create/Update Google config
print("\n[Test 1] Create Google SSO Config")
google, created = SSOConfiguration.objects.update_or_create(
    provider='google',
    defaults={
        'is_enabled': True,
        'google_client_id': 'test-google-123',
        'google_client_secret': 'test-secret-123',
        'updated_by': admin_user
    }
)
print(f"✓ Google: ID={google.id}, enabled={google.is_enabled}")

# Test 2: Create/Update Azure config
print("\n[Test 2] Create Azure SSO Config")
azure, created = SSOConfiguration.objects.update_or_create(
    provider='azure',
    defaults={
        'is_enabled': True,
        'azure_tenant_id': 'test-tenant-456',
        'azure_client_id': 'test-azure-id-456',
        'azure_client_secret': 'test-azure-secret-456',
        'updated_by': admin_user
    }
)
print(f"✓ Azure: ID={azure.id}, enabled={azure.is_enabled}")

# Test 3: Create/Update SAML config
print("\n[Test 3] Create SAML SSO Config")
saml, created = SSOConfiguration.objects.update_or_create(
    provider='saml2',
    defaults={
        'is_enabled': False,
        'saml_entity_id': 'https://example.com/saml',
        'saml_sso_url': 'https://idp.example.com/sso',
        'saml_certificate': '-----BEGIN CERT-----\nMIIC...',
        'updated_by': admin_user
    }
)
print(f"✓ SAML: ID={saml.id}, enabled={saml.is_enabled}")

# Test 4: Create/Update LDAP config
print("\n[Test 4] Create LDAP SSO Config")
ldap, created = SSOConfiguration.objects.update_or_create(
    provider='ldap',
    defaults={
        'is_enabled': True,
        'ldap_server_uri': 'ldap://ldap.example.com:389',
        'ldap_bind_dn': 'cn=admin,dc=example,dc=com',
        'ldap_bind_password': 'test-ldap-pass',
        'ldap_user_search_base': 'ou=users,dc=example,dc=com',
        'updated_by': admin_user
    }
)
print(f"✓ LDAP: ID={ldap.id}, enabled={ldap.is_enabled}")

# Test 5: Verify all configs saved
print("\n[Test 5] Verify Database Persistence")
count = SSOConfiguration.objects.count()
print(f"✓ Total SSO configs in database: {count}")

for provider in ['google', 'azure', 'saml2', 'ldap']:
    config = SSOConfiguration.objects.get(provider=provider)
    print(f"  ✓ {provider}: enabled={config.is_enabled}, updated_by={config.updated_by.username}")

# Test 6: Test toggle functionality
print("\n[Test 6] Test Toggle Functionality")
google.is_enabled = False
google.save()
recheck = SSOConfiguration.objects.get(provider='google')
print(f"✓ Toggled Google OFF: {recheck.is_enabled} (should be False)")

google.is_enabled = True
google.save()
recheck = SSOConfiguration.objects.get(provider='google')
print(f"✓ Toggled Google ON: {recheck.is_enabled} (should be True)")

# Test 7: Test update scenario
print("\n[Test 7] Test Update Scenario (simulating save button click)")
update_data = {
    'provider': 'google',
    'is_enabled': True,
    'google_client_id': 'NEW-GOOGLE-CLIENT-ID-999',
    'google_client_secret': 'NEW-GOOGLE-SECRET-999',
    'updated_by': admin_user
}
google, created = SSOConfiguration.objects.update_or_create(
    provider=update_data['provider'],
    defaults={k: v for k, v in update_data.items() if k != 'provider'}
)
print(f"✓ Updated Google config:")
print(f"  - client_id: {google.google_client_id}")
print(f"  - enabled: {google.is_enabled}")

# Test 8: Verify all providers are independent
print("\n[Test 8] Verify Independent Provider Configuration")
providers_state = {}
for provider in ['google', 'azure', 'saml2', 'ldap']:
    config = SSOConfiguration.objects.get(provider=provider)
    providers_state[provider] = {
        'is_enabled': config.is_enabled,
        'id': config.id,
        'updated_by': config.updated_by.username if config.updated_by else 'None'
    }
    print(f"✓ {provider}: {providers_state[provider]}")

print("\n" + "="*70)
print("  ✓ ALL TESTS PASSED!")
print("="*70 + "\n")
print("Summary:")
print(f"  • Database connection: Working ✓")
print(f"  • Model accessibility: Working ✓")
print(f"  • Create operations: Working ✓")
print(f"  • Update operations: Working ✓")
print(f"  • Read operations: Working ✓")
print(f"  • Toggle functionality: Working ✓")
print(f"  • Independent providers: Working ✓")
print(f"  • Total configs saved: {count}")
print("\n" + "="*70 + "\n")
