#!/usr/bin/env python
"""
تطبيق القالب الافتراضي على الفواتير التي لا تملك قالب
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from core.models import SaleInvoice, PurchaseOrder, PrintTemplate

print("تطبيق القالب الافتراضي على الفواتير والأوامر...")

# تطبيق على فواتير المبيعات
default_sales_template = PrintTemplate.objects.filter(
    template_type='sales_invoice',
    is_default=True
).first()

if default_sales_template:
    updated_count = 0
    for invoice in SaleInvoice.objects.filter(print_template__isnull=True):
        invoice.print_template = default_sales_template
        invoice.save()
        updated_count += 1
    print(f"✓ تم تطبيق القالب الافتراضي على {updated_count} فاتورة مبيعات")
else:
    print("✗ لا يوجد قالب افتراضي لفواتير المبيعات")

# تطبيق على أوامر الشراء
default_po_template = PrintTemplate.objects.filter(
    template_type='purchase_order',
    is_default=True
).first()

if default_po_template:
    updated_count = 0
    for po in PurchaseOrder.objects.filter(print_template__isnull=True):
        po.print_template = default_po_template
        po.save()
        updated_count += 1
    print(f"✓ تم تطبيق القالب الافتراضي على {updated_count} أمر شراء")
else:
    print("✗ لا يوجد قالب افتراضي لأوامر الشراء")

print("\n✓ تم إكمال التطبيق!")
