#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from django.test import Client

client = Client()
response = client.get('/reports/?export=pdf&quarter=current')

print(f'Status Code: {response.status_code}')
print(f'Content Type: {response.get("Content-Type", "Not set")}')
print(f'Content Length: {len(response.content)} bytes')

if response.status_code == 200:
    # Check if it's a PDF
    if b'%PDF' in response.content[:20]:
        print('✓ SUCCESS: This is a valid PDF file!')
        print(f'PDF Header: {response.content[:10]}')
    else:
        print('✗ FAILED: Content is not a PDF')
        print(f'Content starts with: {response.content[:100]}')
        if b'CSV' in response.content[:100] or b'invoice' in response.content[:100]:
            print('This appears to be CSV content instead of PDF')
else:
    print(f'✗ ERROR: HTTP {response.status_code}')
    print(f'Response: {response.content[:200]}')
