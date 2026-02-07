#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

client = Client()

# Test 1: Load registration page
print("Test 1: Load registration page")
response = client.get('/register/')
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print("✓ Page loaded successfully")
    # Check if form fields are present
    content = response.content.decode()
    if 'username' in content and 'password1' in content and 'email' in content:
        print("✓ Form fields are present in the page")
    else:
        print("✗ Form fields missing")
else:
    print("✗ Failed to load page")

# Test 2: Try to register a new user
print("\nTest 2: Register a new user")
test_username = f'testuser_{User.objects.count()}'
response = client.post('/register/', {
    'username': test_username,
    'first_name': 'Test',
    'last_name': 'User',
    'email': f'{test_username}@example.com',
    'password1': 'SecurePass123!',
    'password2': 'SecurePass123!',
})

print(f"Status: {response.status_code}")
if response.status_code == 302:
    print("✓ Registration successful (redirect to dashboard)")
    # Check if user was created in database
    user_exists = User.objects.filter(username=test_username).exists()
    if user_exists:
        print("✓ User created in database")
        user = User.objects.get(username=test_username)
        print(f"  - Username: {user.username}")
        print(f"  - Email: {user.email}")
        print(f"  - First Name: {user.first_name}")
        print(f"  - Last Name: {user.last_name}")
        # Clean up
        user.delete()
        print("✓ Test user cleaned up")
    else:
        print("✗ User not created in database")
else:
    print(f"✗ Registration failed with status {response.status_code}")
