#!/usr/bin/env python
"""
اختبار التحقق من إصلاح نماذج الطباعة
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from core.models import SaleInvoice, PrintTemplate, PurchaseOrder
from datetime import date

print("=" * 80)
print("اختبار إصلاح نماذج الطباعة")
print("=" * 80)

# 1. التحقق من وجود قالب افتراضي
print("\n1. التحقق من القالب الافتراضي:")
default_sales_template = PrintTemplate.objects.filter(
    template_type='sales_invoice',
    is_default=True
).first()

if default_sales_template:
    print(f"✓ وجد قالب افتراضي لفواتير المبيعات: {default_sales_template.name}")
else:
    print("✗ لا يوجد قالب افتراضي لفواتير المبيعات")

default_po_template = PrintTemplate.objects.filter(
    template_type='purchase_order',
    is_default=True
).first()

if default_po_template:
    print(f"✓ وجد قالب افتراضي لأوامر الشراء: {default_po_template.name}")
else:
    print("✗ لا يوجد قالب افتراضي لأوامر الشراء")

# 2. التحقق من الفواتير الحديثة
print("\n2. التحقق من الفواتير الحديثة:")
recent_invoices = SaleInvoice.objects.all().order_by('-issued_date')[:3]

for invoice in recent_invoices:
    template_name = invoice.print_template.name if invoice.print_template else "بلا قالب"
    print(f"  • الفاتورة {invoice.number}: النموذج = {template_name}")

# 3. التحقق من الحقول الجديدة
print("\n3. التحقق من الحقول الجديدة:")
if recent_invoices.exists():
    first_invoice = recent_invoices.first()
    print(f"  • الحقل 'notes': {repr(first_invoice.notes)}")
    print(f"  • الحقل 'includes_vat': {first_invoice.includes_vat}")
    print(f"  • الحقل 'print_template': {first_invoice.print_template}")
    
    # التحقق من الطرق الجديدة
    print("\n4. التحقق من طرق الحساب:")
    try:
        subtotal = first_invoice.get_subtotal()
        vat_amount = first_invoice.get_vat_amount()
        total = first_invoice.get_total()
        print(f"  ✓ get_subtotal(): {subtotal}")
        print(f"  ✓ get_vat_amount(): {vat_amount}")
        print(f"  ✓ get_total(): {total}")
    except Exception as e:
        print(f"  ✗ خطأ في الطرق: {e}")

# 5. عرض الإحصائيات
print("\n5. الإحصائيات:")
total_invoices = SaleInvoice.objects.count()
invoices_with_template = SaleInvoice.objects.exclude(print_template__isnull=True).count()
invoices_with_notes = SaleInvoice.objects.exclude(notes='').count()
invoices_with_vat = SaleInvoice.objects.filter(includes_vat=True).count()

print(f"  • إجمالي الفواتير: {total_invoices}")
print(f"  • الفواتير بها قالب: {invoices_with_template}")
print(f"  • الفواتير بها ملاحظات: {invoices_with_notes}")
print(f"  • الفواتير تشمل ضريبة: {invoices_with_vat}")

print("\n" + "=" * 80)
print("اختبار مكتمل!")
print("=" * 80)
