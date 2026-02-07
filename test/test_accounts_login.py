#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

# Get the test user
test_user = User.objects.filter(is_staff=True).first()

if test_user:
    # Test 1: Without login (should redirect to login)
    client = Client()
    response = client.get('/accounts/')
    print(f"Test 1 - Without login:")
    print(f"  Status: {response.status_code}")
    if response.status_code == 302:
        print(f"  Redirect to: {response.url}")
    
    # Test 2: With login (should show accounts page)
    client.force_login(test_user)
    response = client.get('/accounts/')
    print(f"\nTest 2 - With login:")
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        print(f"  ✓ Accounts page loaded successfully!")
    else:
        print(f"  ✗ Error: {response.status_code}")
else:
    print('No staff users found')
