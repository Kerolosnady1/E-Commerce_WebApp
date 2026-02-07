#!/usr/bin/env python
"""
اختبار POST request لتطبيق القالب على فاتورة محددة
"""
import os
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from django.test import Client
from core.models import SaleInvoice, PrintTemplate

# Create client
client = Client()

# Get a template
template = PrintTemplate.objects.filter(template_type='sales_invoice').first()
invoice = SaleInvoice.objects.first()

if template and invoice:
    print(f"اختبار تطبيق القالب:")
    print(f"  • الفاتورة: {invoice.number}")
    print(f"  • القالب الحالي: {invoice.print_template}")
    print(f"  • القالب المراد تطبيقه: {template.name}")
    
    # Test POST request
    response = client.post('/print-templates/', 
        json.dumps({
            'template_id': template.id,
            'template_type': 'sales_invoice',
            'document_id': invoice.id,
        }),
        content_type='application/json'
    )
    
    print(f"\n  • Response Status: {response.status_code}")
    print(f"  • Response: {response.json()}")
    
    # Refresh invoice from DB
    invoice.refresh_from_db()
    print(f"\n  • القالب الجديد: {invoice.print_template}")
    
    if invoice.print_template.id == template.id:
        print("\n✓ تم تطبيق القالب بنجاح!")
    else:
        print("\n✗ فشل تطبيق القالب")
else:
    print("✗ لم يتم العثور على قالب أو فاتورة")
