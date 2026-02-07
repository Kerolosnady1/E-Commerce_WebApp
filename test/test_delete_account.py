#!/usr/bin/env python
"""
Test script to verify delete_account functionality
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from core.models import UserProfile, UserSession, SecurityLog

# Create a test user (delete first if exists)
User.objects.filter(username='test_delete_user').delete()

test_user = User.objects.create_user(
    username='test_delete_user',
    email='test_delete@example.com',
    password='TestPassword123!'
)

print(f"✓ Created test user: {test_user.username}")

# Verify UserProfile exists
profile, created = UserProfile.objects.get_or_create(user=test_user)
if created:
    print(f"✓ Created UserProfile: {profile.id}")
else:
    print(f"✓ UserProfile exists: {profile.id}")

# Create a test session
session = UserSession.objects.create(
    user=test_user,
    session_key='test_session_key_12345'
)
print(f"✓ Created UserSession: {session.id}")

# Create a security log
log = SecurityLog.objects.create(
    user=test_user,
    action='test_action',
    ip_address='127.0.0.1'
)
print(f"✓ Created SecurityLog: {log.id}")

# Verify counts before deletion
user_id = test_user.id
profile_count_before = UserProfile.objects.filter(user=test_user).count()
session_count_before = UserSession.objects.filter(user=test_user).count()
log_count_before = SecurityLog.objects.filter(user=test_user).count()

print(f"\nBefore deletion:")
print(f"  - UserProfiles: {profile_count_before}")
print(f"  - UserSessions: {session_count_before}")
print(f"  - SecurityLogs: {log_count_before}")

# Test the delete_account view
client = Client()

# Try to access without authentication
response = client.get('/profile/delete-account/')
print(f"\nGET /profile/delete-account/ (not authenticated): {response.status_code}")
if response.status_code == 302:
    print("  ✓ Redirected to login (expected)")
else:
    print(f"  ✗ Expected 302, got {response.status_code}")

# Login and test
client.login(username='test_delete_user', password='TestPassword123!')
response = client.get('/profile/delete-account/')
print(f"\nGET /profile/delete-account/ (authenticated): {response.status_code}")
if response.status_code == 200:
    print("  ✓ Page loaded successfully")
else:
    print(f"  ✗ Expected 200, got {response.status_code}")

# Test with wrong password
response = client.post('/profile/delete-account/', {
    'password': 'WrongPassword',
    'confirm_delete': 'على_علم_تام'
})
print(f"\nPOST with wrong password: {response.status_code}")
test_user_still_exists = User.objects.filter(id=user_id).exists()
if test_user_still_exists:
    print("  ✓ User NOT deleted (wrong password rejected)")
else:
    print("  ✗ User was deleted despite wrong password!")

# Test with correct password but wrong confirmation text
client.login(username='test_delete_user', password='TestPassword123!')
response = client.post('/profile/delete-account/', {
    'password': 'TestPassword123!',
    'confirm_delete': 'wrong_text'
})
print(f"\nPOST with wrong confirmation text: {response.status_code}")
test_user_still_exists = User.objects.filter(id=user_id).exists()
if test_user_still_exists:
    print("  ✓ User NOT deleted (wrong confirmation rejected)")
else:
    print("  ✗ User was deleted despite wrong confirmation!")

# Test with correct data - perform actual deletion
client.login(username='test_delete_user', password='TestPassword123!')
response = client.post('/profile/delete-account/', {
    'password': 'TestPassword123!',
    'confirm_delete': 'على_علم_تام'
})
print(f"\nPOST with correct data: {response.status_code}")
if response.status_code == 302:
    print(f"  ✓ Redirected (expected) to {response.url}")
else:
    print(f"  ✗ Expected 302, got {response.status_code}")

# Verify deletion cascade
import time
time.sleep(0.5)  # Brief pause for DB operations

user_exists_after = User.objects.filter(id=user_id).exists()
profile_count_after = UserProfile.objects.filter(user__id=user_id).count()
session_count_after = UserSession.objects.filter(user__id=user_id).count()
log_count_after = SecurityLog.objects.filter(user__id=user_id).count()

print(f"\nAfter deletion:")
print(f"  - User exists: {user_exists_after}")
if not user_exists_after:
    print("    ✓ User deleted successfully")
else:
    print("    ✗ User still exists!")

print(f"  - UserProfiles: {profile_count_after}")
if profile_count_after == 0:
    print("    ✓ UserProfiles deleted (CASCADE)")
else:
    print(f"    ✗ {profile_count_after} UserProfiles still exist!")

print(f"  - UserSessions: {session_count_after}")
if session_count_after == 0:
    print("    ✓ UserSessions deleted (CASCADE)")
else:
    print(f"    ✗ {session_count_after} UserSessions still exist!")

print(f"  - SecurityLogs: {log_count_after}")
if log_count_after == 0:
    print("    ✓ SecurityLogs cleaned (SET_NULL or deleted)")
else:
    print(f"    ⚠ {log_count_after} SecurityLogs remain (may be expected with SET_NULL)")

print("\n" + "="*50)
print("SUMMARY:")
if not user_exists_after and profile_count_after == 0 and session_count_after == 0:
    print("✓ delete_account functionality working correctly!")
else:
    print("✗ Some issues detected - check above")
print("="*50)
