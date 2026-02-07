#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from core.models import Supplier

User = get_user_model()

# Get a test user
test_user = User.objects.filter(is_staff=True).first()

if test_user:
    # Create a test supplier
    supplier = Supplier.objects.create(
        name='مورد اختبار للحذف',
        email='test@supplier.com',
        phone='1234567890'
    )
    print(f"Created supplier: {supplier.name} (ID: {supplier.id})")
    
    # Now try to delete it (without related PO)
    client = Client()
    client.force_login(test_user)
    
    # First GET the confirmation page
    response = client.get(f'/suppliers/{supplier.id}/delete/')
    print(f"\nGET confirmation page status: {response.status_code}")
    
    # Then POST to delete
    response = client.post(f'/suppliers/{supplier.id}/delete/')
    print(f"POST delete status: {response.status_code}")
    print(f"Redirect to: {response.url if response.status_code in [301, 302] else 'N/A'}")
    
    # Check if supplier still exists
    supplier_exists = Supplier.objects.filter(id=supplier.id).exists()
    print(f"Supplier still exists after delete: {supplier_exists}")
    
    if not supplier_exists:
        print("✓ Supplier was successfully deleted!")
    else:
        print("✗ Supplier was NOT deleted")
else:
    print('No staff users found')
