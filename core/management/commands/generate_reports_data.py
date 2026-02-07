from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
from decimal import Decimal
from core.models import Customer, Supplier, Product, SaleInvoice, PurchaseOrder, Category


class Command(BaseCommand):
    help = 'Populate database with realistic sample data for last 7 months'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample data for reports...')
        
        # Ensure we have basic data
        if Customer.objects.count() == 0:
            for i in range(10):
                Customer.objects.create(
                    name=f'عميل {i+1}',
                    email=f'customer{i+1}@example.com',
                    phone=f'05{random.randint(10000000, 99999999)}',
                    balance=Decimal('0.00')
                )
            self.stdout.write('Created 10 customers')
        
        if Supplier.objects.count() == 0:
            for i in range(5):
                Supplier.objects.create(
                    name=f'مورد {i+1}',
                    email=f'supplier{i+1}@example.com',
                    phone=f'011{random.randint(1000000, 9999999)}'
                )
            self.stdout.write('Created 5 suppliers')
        
        if Product.objects.count() < 10:
            products_data = [
                ('لابتوب', 'LAP-001', 3500),
                ('موبايل', 'MOB-001', 2500),
                ('شاشة', 'TV-001', 1800),
                ('كنبة', 'SOF-001', 1500),
                ('طاولة', 'TAB-001', 800),
            ]
            for name, sku, price in products_data:
                Product.objects.get_or_create(
                    sku=sku,
                    defaults={'name': name, 'price': Decimal(str(price))}
                )
            self.stdout.write('Created products')
        
        customers = list(Customer.objects.all())
        suppliers = list(Supplier.objects.all())
        products = list(Product.objects.all())
        
        # Create invoices for last 7 months
        today = timezone.now().date()
        invoice_count = 0
        purchase_count = 0
        
        for month_offset in range(6, -1, -1):  # Start from 6 months ago
            month_date = (today.replace(day=1) - timedelta(days=month_offset*30))
            
            # Create 10-15 sale invoices per month
            for _ in range(random.randint(10, 15)):
                invoice_date = month_date + timedelta(days=random.randint(0, 28))
                customer = random.choice(customers)
                
                # Calculate total
                total = Decimal('0.00')
                for _ in range(random.randint(1, 4)):
                    product = random.choice(products)
                    quantity = random.randint(1, 5)
                    total += product.price * quantity
                
                # Create unique invoice number
                invoice_num = f'INV-{invoice_date.strftime("%Y%m%d")}-{random.randint(100, 999)}'
                
                try:
                    SaleInvoice.objects.create(
                        number=invoice_num,
                        customer=customer,
                        issued_date=invoice_date,
                        due_date=invoice_date + timedelta(days=30),
                        status=random.choice(['paid', 'paid', 'paid', 'pending']),  # 75% paid
                        total=total
                    )
                    invoice_count += 1
                except:
                    pass  # Skip duplicates
            
            # Create 4-6 purchase orders per month
            for _ in range(random.randint(4, 6)):
                order_date = month_date + timedelta(days=random.randint(0, 28))
                supplier = random.choice(suppliers)
                
                # Calculate total (purchase at 60% of sale price)
                total = Decimal('0.00')
                for _ in range(random.randint(2, 5)):
                    product = random.choice(products)
                    quantity = random.randint(5, 20)
                    total += product.price * Decimal('0.6') * quantity
                
                # Create unique PO number
                po_num = f'PO-{order_date.strftime("%Y%m%d")}-{random.randint(100, 999)}'
                
                try:
                    PurchaseOrder.objects.create(
                        number=po_num,
                        supplier=supplier,
                        issued_date=order_date,
                        status=random.choice(['draft', 'sent', 'received']),
                        total=total
                    )
                    purchase_count += 1
                except:
                    pass  # Skip duplicates
        
        self.stdout.write(self.style.SUCCESS(f'✅ Created {invoice_count} sale invoices'))
        self.stdout.write(self.style.SUCCESS(f'✅ Created {purchase_count} purchase orders'))
        self.stdout.write(self.style.SUCCESS(f'Total Revenue: ${SaleInvoice.objects.filter(status="paid").aggregate(total=models.Sum("total"))["total"] or 0}'))
        self.stdout.write(self.style.SUCCESS(f'Total Expenses: ${PurchaseOrder.objects.aggregate(total=models.Sum("total"))["total"] or 0}'))
