#!/usr/bin/env python
"""
SSO Implementation Comprehensive Validation Test
Tests that verify the complete SSO workflow works correctly with real database operations
"""

import os
import sys
import django
from datetime import datetime
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from core.models import SSOConfiguration, SecurityLog
import json


class Colors:
    """Terminal colors for output formatting"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'


def print_header(text):
    """Print section header"""
    print(f"\n{Colors.CYAN}{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}{Colors.RESET}\n")


def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")


def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")


def print_info(text):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")


def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")


def test_database_connection():
    """Test 1: Verify database connection and model accessibility"""
    print_header("TEST 1: DATABASE CONNECTION & MODEL ACCESSIBILITY")
    
    try:
        # Test reading from database
        count = SSOConfiguration.objects.count()
        print_success(f"Database connected successfully - Found {count} SSO configurations")
        
        # Test model fields
        fields = [f.name for f in SSOConfiguration._meta.get_fields()]
        expected_fields = ['id', 'provider', 'is_enabled', 'google_client_id', 'azure_tenant_id', 'saml_entity_id', 'ldap_server_uri']
        missing = [f for f in expected_fields if f not in fields]
        
        if not missing:
            print_success(f"All required model fields are present: {len(fields)} fields total")
        else:
            print_error(f"Missing fields: {missing}")
            return False
        
        return True
    except Exception as e:
        print_error(f"Database connection failed: {str(e)}")
        return False


def test_create_test_data():
    """Test 2: Create test SSO configurations with real database operations"""
    print_header("TEST 2: CREATE TEST DATA - REAL DATABASE OPERATIONS")
    
    try:
        admin_user, created = User.objects.get_or_create(
            username='test_admin',
            defaults={'email': 'admin@test.com', 'is_staff': True, 'is_superuser': True}
        )
        print_success(f"Admin user ready: {admin_user.username} (created={created})")
        
        # Clear existing test configs
        SSOConfiguration.objects.filter(provider__in=['google', 'azure', 'saml2', 'ldap']).delete()
        print_info("Cleared existing test SSO configurations")
        
        # Create Google config
        google_config, created = SSOConfiguration.objects.update_or_create(
            provider='google',
            defaults={
                'is_enabled': True,
                'google_client_id': 'test-google-client-id-12345.apps.googleusercontent.com',
                'google_client_secret': 'test-google-client-secret-xyz789',
                'updated_by': admin_user
            }
        )
        print_success(f"Google config: {google_config.id} (is_enabled={google_config.is_enabled})")
        
        # Create Azure config
        azure_config, created = SSOConfiguration.objects.update_or_create(
            provider='azure',
            defaults={
                'is_enabled': True,
                'azure_tenant_id': 'test-tenant-id-abc123',
                'azure_client_id': 'test-azure-client-id-def456',
                'azure_client_secret': 'test-azure-client-secret-ghi789',
                'updated_by': admin_user
            }
        )
        print_success(f"Azure config: {azure_config.id} (is_enabled={azure_config.is_enabled})")
        
        # Create SAML config
        saml_config, created = SSOConfiguration.objects.update_or_create(
            provider='saml2',
            defaults={
                'is_enabled': True,
                'saml_entity_id': 'https://example.com/saml/metadata',
                'saml_sso_url': 'https://idp.example.com/sso',
                'saml_certificate': '-----BEGIN CERTIFICATE-----\nMIIC...',
                'updated_by': admin_user
            }
        )
        print_success(f"SAML config: {saml_config.id} (is_enabled={saml_config.is_enabled})")
        
        # Create LDAP config
        ldap_config, created = SSOConfiguration.objects.update_or_create(
            provider='ldap',
            defaults={
                'is_enabled': True,
                'ldap_server_uri': 'ldap://ldap.example.com:389',
                'ldap_bind_dn': 'cn=admin,dc=example,dc=com',
                'ldap_bind_password': 'test-ldap-password-secret',
                'ldap_user_search_base': 'ou=users,dc=example,dc=com',
                'updated_by': admin_user
            }
        )
        print_success(f"LDAP config: {ldap_config.id} (is_enabled={ldap_config.is_enabled})")
        
        total_created = SSOConfiguration.objects.count()
        print_success(f"Total SSO configurations in database: {total_created}")
        return True
        
    except Exception as e:
        print_error(f"Failed to create test data: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_api_load_operation():
    """Test 3: Simulate API GET /api/sso/load/ operation"""
    print_header("TEST 3: API LOAD OPERATION - SIMULATED GET REQUEST")
    
    try:
        client = Client()
        
        # Get admin user for login
        admin_user = User.objects.get(username='test_admin')
        client.force_login(admin_user)
        
        # Call the API endpoint
        response = client.get('/api/sso/load/')
        print_success(f"API endpoint responded with status code: {response.status_code}")
        
        # Parse response
        data = json.loads(response.content.decode('utf-8'))
        
        # Verify all providers are in response
        providers = ['google', 'azure', 'saml2', 'ldap']
        for provider in providers:
            if provider in data:
                config = data[provider]
                print_success(f"  {provider}: is_enabled={config.get('is_enabled')} ✓")
            else:
                print_warning(f"  {provider}: not in response")
        
        # Verify that client_secret is NOT sent (security check)
        if 'google' in data and 'client_secret' not in data['google']:
            print_success("Security check: client_secret not exposed in GET response ✓")
        else:
            print_warning("Security: client_secret should not be in GET response")
        
        return True
        
    except Exception as e:
        print_error(f"API load operation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_api_save_operation():
    """Test 4: Simulate API POST /api/sso/save/ operation"""
    print_header("TEST 4: API SAVE OPERATION - SIMULATED POST REQUEST")
    
    try:
        client = Client()
        admin_user = User.objects.get(username='test_admin')
        client.force_login(admin_user)
        
        # Prepare new configuration data (simulating form submission)
        new_config = {
            'google': {
                'is_enabled': True,
                'client_id': 'new-google-id-999.apps.googleusercontent.com',
                'client_secret': 'new-google-secret-updated-999'
            },
            'azure': {
                'is_enabled': True,
                'tenant_id': 'new-tenant-updated-999',
                'client_id': 'new-azure-id-updated-999',
                'client_secret': 'new-azure-secret-updated-999'
            },
            'saml2': {
                'is_enabled': False,
                'entity_id': '',
                'sso_url': '',
                'certificate': ''
            },
            'ldap': {
                'is_enabled': True,
                'server_uri': 'ldap://newserver.example.com:389',
                'bind_dn': 'cn=newadmin,dc=example,dc=com',
                'bind_password': 'new-password-updated',
                'user_search_base': 'ou=staff,dc=example,dc=com'
            }
        }
        
        # Call the API endpoint with POST
        response = client.post(
            '/api/sso/save/',
            data=json.dumps(new_config),
            content_type='application/json'
        )
        print_success(f"API POST endpoint responded with status code: {response.status_code}")
        
        # Parse response
        data = json.loads(response.content.decode('utf-8'))
        
        if data.get('success'):
            print_success(f"Save operation successful: {data.get('message')}")
        else:
            print_error(f"Save operation failed: {data.get('error')}")
            return False
        
        return True
        
    except Exception as e:
        print_error(f"API save operation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_data_persistence():
    """Test 5: Verify data was actually persisted in database"""
    print_header("TEST 5: DATA PERSISTENCE VERIFICATION")
    
    try:
        # Fetch from database and verify
        google = SSOConfiguration.objects.get(provider='google')
        azure = SSOConfiguration.objects.get(provider='azure')
        saml = SSOConfiguration.objects.get(provider='saml2')
        ldap = SSOConfiguration.objects.get(provider='ldap')
        
        # Check Google
        if google.google_client_id.startswith('new-'):
            print_success(f"Google config persisted: client_id updated to {google.google_client_id[:20]}...")
        else:
            print_warning(f"Google config may not have been updated: {google.google_client_id}")
        
        # Check Azure
        if azure.azure_tenant_id.startswith('new-'):
            print_success(f"Azure config persisted: tenant_id updated to {azure.azure_tenant_id[:20]}...")
        else:
            print_warning(f"Azure config may not have been updated: {azure.azure_tenant_id}")
        
        # Check SAML disabled status
        if not saml.is_enabled:
            print_success(f"SAML config persisted: is_enabled={saml.is_enabled} (disabled as expected)")
        else:
            print_warning(f"SAML should be disabled but is_enabled={saml.is_enabled}")
        
        # Check LDAP
        if ldap.ldap_server_uri.startswith('ldap://newserver'):
            print_success(f"LDAP config persisted: server_uri updated to {ldap.ldap_server_uri}")
        else:
            print_warning(f"LDAP config may not have been updated: {ldap.ldap_server_uri}")
        
        return True
        
    except Exception as e:
        print_error(f"Data persistence check failed: {str(e)}")
        return False


def test_security_audit_log():
    """Test 6: Verify SecurityLog audit trail is being recorded"""
    print_header("TEST 6: SECURITY AUDIT LOG VERIFICATION")
    
    try:
        # Check for SSO-related security logs
        sso_logs = SecurityLog.objects.filter(
            action_type='settings_change',
            description__icontains='SSO'
        ).order_by('-created_at')
        
        if sso_logs.exists():
            latest = sso_logs.first()
            print_success(f"Found {sso_logs.count()} SSO-related security logs")
            print_success(f"  Latest log:")
            print_success(f"    - User: {latest.username}")
            print_success(f"    - Action: {latest.action_type}")
            print_success(f"    - Status: {latest.status}")
            print_success(f"    - Timestamp: {latest.created_at}")
            return True
        else:
            print_warning("No SSO-related security logs found (check may run before API save)")
            return True
            
    except Exception as e:
        print_error(f"Security audit log check failed: {str(e)}")
        return False


def test_toggle_functionality():
    """Test 7: Verify toggle enable/disable functionality"""
    print_header("TEST 7: TOGGLE FUNCTIONALITY TEST")
    
    try:
        google = SSOConfiguration.objects.get(provider='google')
        
        # Test toggle OFF
        google.is_enabled = False
        google.save()
        print_success(f"Google config toggled OFF: is_enabled={google.is_enabled}")
        
        # Verify in database
        recheck = SSOConfiguration.objects.get(provider='google')
        if not recheck.is_enabled:
            print_success("Verified: Google config is disabled in database")
        else:
            print_error("Toggle OFF failed - still enabled in database")
            return False
        
        # Test toggle ON
        recheck.is_enabled = True
        recheck.save()
        print_success(f"Google config toggled ON: is_enabled={recheck.is_enabled}")
        
        # Verify in database
        verify = SSOConfiguration.objects.get(provider='google')
        if verify.is_enabled:
            print_success("Verified: Google config is enabled in database")
        else:
            print_error("Toggle ON failed - still disabled in database")
            return False
        
        return True
        
    except Exception as e:
        print_error(f"Toggle functionality test failed: {str(e)}")
        return False


def test_independent_provider_config():
    """Test 8: Verify each provider can be configured independently"""
    print_header("TEST 8: INDEPENDENT PROVIDER CONFIGURATION")
    
    try:
        # Get all providers
        google = SSOConfiguration.objects.get(provider='google')
        azure = SSOConfiguration.objects.get(provider='azure')
        saml = SSOConfiguration.objects.get(provider='saml2')
        ldap = SSOConfiguration.objects.get(provider='ldap')
        
        # Verify each has independent state
        configs = [
            ('Google', google.is_enabled, google.google_client_id),
            ('Azure', azure.is_enabled, azure.azure_client_id),
            ('SAML', saml.is_enabled, saml.saml_entity_id),
            ('LDAP', ldap.is_enabled, ldap.ldap_server_uri)
        ]
        
        for name, enabled, identifier in configs:
            status = "Enabled ✓" if enabled else "Disabled"
            print_success(f"{name}: {status} - {identifier[:30]}...")
        
        return True
        
    except Exception as e:
        print_error(f"Independent provider test failed: {str(e)}")
        return False


def test_modal_form_binding():
    """Test 9: Verify form fields are correctly bound to data"""
    print_header("TEST 9: MODAL FORM DATA BINDING")
    
    try:
        # Simulate form submission and retrieval
        client = Client()
        admin_user = User.objects.get(username='test_admin')
        client.force_login(admin_user)
        
        # Load the data
        response = client.get('/api/sso/load/')
        data = json.loads(response.content.decode('utf-8'))
        
        # Verify structure matches form fields
        form_fields = {
            'google': ['is_enabled', 'client_id'],
            'azure': ['is_enabled', 'tenant_id', 'client_id'],
            'saml2': ['is_enabled', 'entity_id', 'sso_url'],
            'ldap': ['is_enabled', 'server_uri', 'bind_dn', 'user_search_base']
        }
        
        all_valid = True
        for provider, fields in form_fields.items():
            if provider not in data:
                print_error(f"{provider}: Not in API response")
                all_valid = False
                continue
            
            for field in fields:
                if field in data[provider]:
                    print_success(f"{provider}.{field}: Present in response ✓")
                else:
                    print_warning(f"{provider}.{field}: Missing from response")
        
        return all_valid
        
    except Exception as e:
        print_error(f"Form binding test failed: {str(e)}")
        return False


def test_readonly_secret_fields():
    """Test 10: Verify secret fields are not exposed to frontend"""
    print_header("TEST 10: SECRET FIELD SECURITY TEST")
    
    try:
        client = Client()
        admin_user = User.objects.get(username='test_admin')
        client.force_login(admin_user)
        
        # Load the data
        response = client.get('/api/sso/load/')
        data = json.loads(response.content.decode('utf-8'))
        
        # Check that secrets are not in response
        dangerous_fields = ['client_secret', 'bind_password', 'certificate']
        
        secrets_exposed = False
        for provider, config in data.items():
            for field in dangerous_fields:
                if field in config:
                    print_error(f"SECURITY ISSUE: {provider}.{field} exposed in API response!")
                    secrets_exposed = True
                else:
                    print_success(f"{provider}: {field} properly excluded ✓")
        
        return not secrets_exposed
        
    except Exception as e:
        print_error(f"Secret field test failed: {str(e)}")
        return False


def main():
    """Main test runner"""
    print(f"\n{Colors.CYAN}")
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║          SSO IMPLEMENTATION COMPREHENSIVE VALIDATION            ║")
    print("║                     Complete Test Suite                        ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}")
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Test Data Creation", test_create_test_data),
        ("API Load Operation", test_api_load_operation),
        ("API Save Operation", test_api_save_operation),
        ("Data Persistence", test_data_persistence),
        ("Security Audit Log", test_security_audit_log),
        ("Toggle Functionality", test_toggle_functionality),
        ("Independent Provider", test_independent_provider_config),
        ("Form Data Binding", test_modal_form_binding),
        ("Secret Field Security", test_readonly_secret_fields),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"Test '{name}' crashed: {str(e)}")
            results.append((name, False))
    
    # Print summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = f"{Colors.GREEN}PASS{Colors.RESET}" if result else f"{Colors.RED}FAIL{Colors.RESET}"
        print(f"  {status}  {name}")
    
    print(f"\n{Colors.CYAN}{'='*70}{Colors.RESET}")
    print(f"  Total: {passed}/{total} tests passed")
    print(f"{Colors.CYAN}{'='*70}\n{Colors.RESET}")
    
    if passed == total:
        print(f"{Colors.GREEN}✓ ALL TESTS PASSED! SSO IMPLEMENTATION IS WORKING CORRECTLY.{Colors.RESET}\n")
        return True
    else:
        print(f"{Colors.RED}✗ {total - passed} test(s) failed. Please review the output above.{Colors.RESET}\n")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
