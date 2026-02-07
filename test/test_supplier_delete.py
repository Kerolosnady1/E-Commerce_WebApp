#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from core.models import Supplier, PurchaseOrder

User = get_user_model()

# Get a test user
test_user = User.objects.filter(is_staff=True).first()

if test_user:
    # Create a test supplier
    supplier = Supplier.objects.create(
        name='مورد اختبار',
        email='test@supplier.com',
        phone='1234567890'
    )
    print(f"Created supplier: {supplier.name} (ID: {supplier.id})")
    
    # Create a purchase order for this supplier
    from datetime import date
    po = PurchaseOrder.objects.create(
        number=f'PO-TEST-{supplier.id}',
        supplier=supplier,
        issued_date=date.today(),
        status='draft',
        total=100
    )
    print(f"Created purchase order: {po.number}")
    
    # Now try to delete the supplier
    client = Client()
    client.force_login(test_user)
    
    response = client.post(f'/suppliers/{supplier.id}/delete/')
    print(f"\nDelete attempt status: {response.status_code}")
    print(f"Redirect to: {response.url if response.status_code in [301, 302] else 'N/A'}")
    
    # Check if supplier still exists
    supplier_exists = Supplier.objects.filter(id=supplier.id).exists()
    print(f"Supplier still exists: {supplier_exists}")
    
    # Clean up
    po.delete()
    supplier.delete()
    print("\nCleaned up test data")
else:
    print('No staff users found')
