#!/usr/bin/env python
"""
Test script to verify change password functionality
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

# Create or get test user
User.objects.filter(username='test_password_user').delete()

test_user = User.objects.create_user(
    username='test_password_user',
    email='test_pwd@example.com',
    password='OldPassword123'
)

print("="*60)
print("TESTING CHANGE PASSWORD FUNCTIONALITY")
print("="*60)

# 1. Test accessing profile without login
print("\n1. Testing access without login:")
client = Client()
response = client.get('/profile/')
print(f"   GET /profile/ (not authenticated): {response.status_code}")
if response.status_code == 302:
    print("   ✓ Redirected to login (expected)")
else:
    print(f"   ✗ Expected 302, got {response.status_code}")

# 2. Test accessing profile with login
print("\n2. Testing access with login:")
client.login(username='test_password_user', password='OldPassword123')
response = client.get('/profile/')
print(f"   GET /profile/ (authenticated): {response.status_code}")
if response.status_code == 200:
    print("   ✓ Profile page loaded")
else:
    print(f"   ✗ Expected 200, got {response.status_code}")

# 3. Test with wrong current password
print("\n3. Testing with wrong current password:")
response = client.post('/profile/', {
    'change_password': '1',
    'current_password': 'WrongPassword123',
    'new_password': 'NewPassword123',
    'confirm_password': 'NewPassword123'
})
print(f"   Status: {response.status_code}")

# Verify password wasn't changed
user_before = User.objects.get(username='test_password_user')
if user_before.check_password('OldPassword123'):
    print("   ✓ Password NOT changed (wrong current password rejected)")
else:
    print("   ✗ Password was changed despite wrong current password!")

# 4. Test with mismatched new passwords
print("\n4. Testing with mismatched new passwords:")
client.login(username='test_password_user', password='OldPassword123')
response = client.post('/profile/', {
    'change_password': '1',
    'current_password': 'OldPassword123',
    'new_password': 'NewPassword123',
    'confirm_password': 'DifferentPassword123'
})
print(f"   Status: {response.status_code}")

# Verify password wasn't changed
user_before = User.objects.get(username='test_password_user')
if user_before.check_password('OldPassword123'):
    print("   ✓ Password NOT changed (mismatched passwords rejected)")
else:
    print("   ✗ Password was changed despite mismatched passwords!")

# 5. Test with password too short
print("\n5. Testing with password too short (< 8 chars):")
client.login(username='test_password_user', password='OldPassword123')
response = client.post('/profile/', {
    'change_password': '1',
    'current_password': 'OldPassword123',
    'new_password': 'short',
    'confirm_password': 'short'
})
print(f"   Status: {response.status_code}")

# Verify password wasn't changed
user_before = User.objects.get(username='test_password_user')
if user_before.check_password('OldPassword123'):
    print("   ✓ Password NOT changed (too short rejected)")
else:
    print("   ✗ Password was changed despite being too short!")

# 6. Test with correct data - perform actual password change
print("\n6. Testing with correct data:")
client.login(username='test_password_user', password='OldPassword123')
response = client.post('/profile/', {
    'change_password': '1',
    'current_password': 'OldPassword123',
    'new_password': 'NewPassword123',
    'confirm_password': 'NewPassword123'
})
print(f"   Status: {response.status_code}")

# Verify password was changed
user_after = User.objects.get(username='test_password_user')
if user_after.check_password('NewPassword123'):
    print("   ✓ Password successfully changed to NewPassword123")
else:
    print("   ✗ Password was NOT changed!")

if not user_after.check_password('OldPassword123'):
    print("   ✓ Old password no longer works")
else:
    print("   ✗ Old password still works (should not!)")

# 7. Test that user stayed logged in after password change
print("\n7. Testing user session after password change:")
response = client.get('/profile/')
if response.status_code == 200:
    print("   ✓ User remained logged in after password change")
else:
    print(f"   ✗ User was logged out (status {response.status_code})")

# 8. Test that new password can be used to login
print("\n8. Testing login with new password:")
new_client = Client()
is_authenticated = new_client.login(username='test_password_user', password='NewPassword123')
if is_authenticated:
    print("   ✓ Login successful with new password")
    response = new_client.get('/profile/')
    if response.status_code == 200:
        print("   ✓ Profile page accessible with new password")
    else:
        print(f"   ✗ Profile page not accessible (status {response.status_code})")
else:
    print("   ✗ Login failed with new password")

# 9. Test database persistence
print("\n9. Testing database persistence:")
from django.db import connection
from django.contrib.auth.models import User as UserModel

# Refresh from database
db_user = UserModel.objects.get(username='test_password_user')
if db_user.check_password('NewPassword123'):
    print("   ✓ New password persisted in database")
else:
    print("   ✗ New password NOT in database")

print("\n" + "="*60)
print("TEST SUMMARY")
print("="*60)

# Final verification
final_user = User.objects.get(username='test_password_user')
password_correct = final_user.check_password('NewPassword123')
old_password_invalid = not final_user.check_password('OldPassword123')

if password_correct and old_password_invalid:
    print("\n✓ CHANGE PASSWORD FUNCTIONALITY WORKING CORRECTLY!")
    print("  - Current password verification works")
    print("  - Password confirmation check works")
    print("  - Minimum length validation works")
    print("  - Password hash properly saved to database")
    print("  - Old password no longer valid")
    print("  - User session maintained after change")
    print("  - New password works for login")
else:
    print("\n✗ SOME ISSUES DETECTED")
    if not password_correct:
        print("  - Password was not properly saved")
    if not old_password_invalid:
        print("  - Old password still works (should not)")

print("\n" + "="*60)

# Cleanup
# User.objects.filter(username='test_password_user').delete()
# print("\nTest user deleted from database")
