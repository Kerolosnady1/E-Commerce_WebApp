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
    client = Client()
    client.force_login(test_user)
    
    try:
        response = client.get('/accounts/')
        print(f'Status Code: {response.status_code}')
        if response.status_code == 200:
            print('✓ SUCCESS: Accounts page loaded successfully!')
        else:
            print(f'✗ Error: HTTP {response.status_code}')
            print(f'Response: {response.content[:200]}')
    except Exception as e:
        print(f'✗ Exception: {e}')
        import traceback
        traceback.print_exc()
else:
    print('No staff users found')
