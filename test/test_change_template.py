#!/usr/bin/env python
"""
اختبار تغيير القالب لفاتورة معينة
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

# Get templates
templates = PrintTemplate.objects.filter(template_type='sales_invoice')
invoice = SaleInvoice.objects.first()

if templates.count() >= 2 and invoice:
    # Get the thermal template (different from default)
    thermal_template = templates.filter(style='thermal').first()
    
    if thermal_template:
        print(f"اختبار تغيير القالب:")
        print(f"  • الفاتورة: {invoice.number}")
        print(f"  • القالب الحالي: {invoice.print_template.name if invoice.print_template else 'بلا قالب'}")
        print(f"  • القالب الجديد: {thermal_template.name}")
        
        # Apply the thermal template
        response = client.post('/print-templates/', 
            json.dumps({
                'template_id': thermal_template.id,
                'template_type': 'sales_invoice',
                'document_id': invoice.id,
            }),
            content_type='application/json'
        )
        
        print(f"\n  • Response: {response.json()}")
        
        # Refresh invoice from DB
        invoice.refresh_from_db()
        print(f"  • القالب بعد التحديث: {invoice.print_template.name}")
        
        if invoice.print_template.id == thermal_template.id:
            print("\n✓✓✓ تم تغيير القالب بنجاح!")
        else:
            print("\n✗ فشل تغيير القالب")
    else:
        print("✗ لم يتم العثور على قالب حراري")
else:
    print("✗ عدد القوالب غير كافٍ للاختبار")
