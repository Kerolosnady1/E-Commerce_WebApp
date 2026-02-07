#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from core.models import SaleInvoice, PrintTemplate, CompanySettings

print("=" * 60)
print("TESTING INVOICE FIELDS & MODELS")
print("=" * 60)

# Check models
inv = SaleInvoice.objects.first()
if inv:
    print(f"\n✓ First Invoice: {inv.number}")
    print(f"  - Notes: '{inv.notes}'")
    print(f"  - Includes VAT: {inv.includes_vat}")
    print(f"  - Print Template: {inv.print_template}")
else:
    print("✗ No invoices in database")

# Check methods
print(f"\n✓ Invoice Methods:")
print(f"  - Has get_subtotal: {hasattr(inv, 'get_subtotal') if inv else 'N/A'}")
print(f"  - Has get_vat_amount: {hasattr(inv, 'get_vat_amount') if inv else 'N/A'}")
print(f"  - Has get_total: {hasattr(inv, 'get_total') if inv else 'N/A'}")

# Check print templates
count = PrintTemplate.objects.count()
print(f"\n✓ Print Templates: {count}")
if count > 0:
    for tmpl in PrintTemplate.objects.all()[:3]:
        print(f"  - {tmpl.name} ({tmpl.get_template_type_display()})")

# Check settings
settings = CompanySettings.objects.first()
if settings:
    print(f"\n✓ Company Settings:")
    print(f"  - VAT Number: {settings.vat_number}")
    print(f"  - Tax Enabled: {settings.tax_enabled}")
    print(f"  - Default Tax Rate: {settings.default_tax_rate}%")
    print(f"  - Prices Include Tax: {settings.prices_include_tax}")
else:
    print("\n✗ No company settings")

print("\n" + "=" * 60)
