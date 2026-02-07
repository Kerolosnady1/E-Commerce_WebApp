"""
Management command to create default print templates
"""
from django.core.management.base import BaseCommand
from core.models import PrintTemplate


class Command(BaseCommand):
    help = 'Create default print templates for invoices and documents'

    def handle(self, *args, **options):
        templates = [
            {
                'name': 'نموذج قياسي (A4)',
                'template_type': 'sales_invoice',
                'style': 'standard',
                'is_active': True,
                'is_default': True,
                'show_qr_code': True,
                'show_signature': True,
                'show_vat': True,
                'header_title': 'فاتورة ضريبية',
            },
            {
                'name': 'حراري / نقاط البيع',
                'template_type': 'sales_invoice',
                'style': 'thermal',
                'is_active': True,
                'is_default': False,
                'show_qr_code': True,
                'show_signature': False,
                'show_vat': True,
                'header_title': 'فاتورة مبيعات',
            },
            {
                'name': 'نموذج عصري (مبسط)',
                'template_type': 'sales_invoice',
                'style': 'minimal',
                'is_active': True,
                'is_default': False,
                'show_qr_code': False,
                'show_signature': True,
                'show_vat': True,
                'header_title': 'فاتورة',
            },
            {
                'name': 'أمر شراء قياسي',
                'template_type': 'purchase_order',
                'style': 'standard',
                'is_active': True,
                'is_default': True,
                'show_qr_code': False,
                'show_signature': True,
                'show_vat': True,
                'header_title': 'أمر شراء',
            },
            {
                'name': 'تقرير المخزون',
                'template_type': 'inventory_report',
                'style': 'standard',
                'is_active': True,
                'is_default': True,
                'show_qr_code': False,
                'show_signature': False,
                'show_vat': False,
                'header_title': 'تقرير المخزون',
            },
            {
                'name': 'بيان العميل',
                'template_type': 'customer_statement',
                'style': 'standard',
                'is_active': True,
                'is_default': True,
                'show_qr_code': False,
                'show_signature': False,
                'show_vat': True,
                'header_title': 'بيان العميل',
            },
        ]

        for template_data in templates:
            template, created = PrintTemplate.objects.get_or_create(
                name=template_data['name'],
                template_type=template_data['template_type'],
                defaults=template_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ تم إنشاء نموذج: {template.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠ النموذج موجود بالفعل: {template.name}')
                )

        self.stdout.write(
            self.style.SUCCESS('✓ تم إنشاء جميع نماذج الطباعة بنجاح!')
        )
