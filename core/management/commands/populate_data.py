from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
from decimal import Decimal
from core.models import Customer, Supplier, Product, SaleInvoice, PurchaseOrder, Category


class Command(BaseCommand):
    help = 'Populate database with realistic sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample data...')
        
        # Create categories
        categories = []
        category_names = ['إلكترونيات', 'أثاث', 'ملابس', 'أغذية', 'أدوات منزلية']
        for name in category_names:
            cat, _ = Category.objects.get_or_create(name=name)
            categories.append(cat)
        
        # Create customers
        customers = []
        customer_names = [
            'أحمد محمد', 'فاطمة علي', 'خالد سعيد', 'نورة عبدالله',
            'عمر حسن', 'سارة إبراهيم', 'يوسف أحمد', 'مريم خالد',
            'عبدالرحمن محمود', 'ليلى فهد'
        ]
        for i, name in enumerate(customer_names):
            customer, _ = Customer.objects.get_or_create(
                name=name,
                defaults={
                    'email': f'customer{i+1}@example.com',
                    'phone': f'05{random.randint(10000000, 99999999)}',
                    'address': f'الرياض، حي {random.choice(["النخيل", "الملك فهد", "العليا", "السليمانية"])}',
                    'balance': Decimal('0.00'),
                    'is_active': True
                }
            )
            customers.append(customer)
        
        # Create suppliers
        suppliers = []
        supplier_names = [
            'مؤسسة التقنية المتقدمة', 'شركة الأثاث الحديث', 'مصنع النسيج الوطني',
            'شركة المواد الغذائية', 'مؤسسة الأدوات المنزلية'
        ]
        for i, name in enumerate(supplier_names):
            supplier, _ = Supplier.objects.get_or_create(
                name=name,
                defaults={
                    'contact_person': f'مدير المبيعات {i+1}',
                    'email': f'supplier{i+1}@example.com',
                    'phone': f'011{random.randint(1000000, 9999999)}',
                    'address': f'جدة، شارع {random.choice(["فلسطين", "التحلية", "الأمير سلطان"])}',
                    'is_active': True
                }
            )
            suppliers.append(supplier)
        
        # Create products
        products = []
        product_data = [
            ('لابتوب ديل', 3500, 'إلكترونيات'),
            ('آيفون 15 برو', 4200, 'إلكترونيات'),
            ('شاشة سامسونج 55"', 2100, 'إلكترونيات'),
            ('كنبة زاوية', 1800, 'أثاث'),
            ('طاولة طعام', 900, 'أثاث'),
            ('ثوب رجالي', 280, 'ملابس'),
            ('عباية نسائية', 350, 'ملابس'),
            ('قهوة عربية', 85, 'أغذية'),
            ('تمر فاخر', 120, 'أغذية'),
            ('طقم أواني', 450, 'أدوات منزلية')
        ]
        
        for name, price, cat_name in product_data:
            category = next(c for c in categories if c.name == cat_name)
            product, _ = Product.objects.get_or_create(
                name=name,
                defaults={
                    'description': f'منتج عالي الجودة - {name}',
                    'price': Decimal(str(price)),
                    'cost': Decimal(str(price * 0.6)),  # Cost is 60% of price
                    'sku': f'SKU-{random.randint(1000, 9999)}',
                    'category': category,
                    'stock': random.randint(10, 100),
                    'is_active': True
                }
            )
            products.append(product)
        
        # Create purchase orders (expenses) for last 7 months
        today = timezone.now().date()
        for month_offset in range(7):
            month_date = (today.replace(day=1) - timedelta(days=month_offset*30))
            
            # 3-5 purchase orders per month
            for _ in range(random.randint(3, 5)):
                order_date = month_date + timedelta(days=random.randint(0, 28))
                supplier = random.choice(suppliers)
                
                # Create purchase order
                po = PurchaseOrder.objects.create(
                    number=f'PO-{order_date.strftime("%Y%m")}-{random.randint(100, 999)}',
                    supplier=supplier,
                    order_date=order_date,
                    expected_date=order_date + timedelta(days=random.randint(3, 10)),
                    status=random.choice(['pending', 'approved', 'received']),
                    notes=f'طلب شراء من {supplier.name}',
                    total=Decimal('0.00')
                )
                
                # Add 2-4 items to each purchase order
                total = Decimal('0.00')
                for _ in range(random.randint(2, 4)):
                    product = random.choice(products)
                    quantity = random.randint(5, 20)
                    unit_price = product.cost
                    subtotal = unit_price * quantity
                    total += subtotal
                
                po.total = total
                po.save()
        
        # Create sale invoices for last 7 months
        for month_offset in range(7):
            month_date = (today.replace(day=1) - timedelta(days=month_offset*30))
            
            # 8-15 invoices per month
            for _ in range(random.randint(8, 15)):
                invoice_date = month_date + timedelta(days=random.randint(0, 28))
                customer = random.choice(customers)
                
                # Create invoice
                invoice = SaleInvoice.objects.create(
                    number=f'INV-{invoice_date.strftime("%Y%m")}-{random.randint(1000, 9999)}',
                    customer=customer,
                    issued_date=invoice_date,
                    due_date=invoice_date + timedelta(days=random.randint(7, 30)),
                    status=random.choice(['paid', 'paid', 'paid', 'pending', 'overdue']),  # 60% paid
                    notes=f'فاتورة بيع - {customer.name}',
                    total=Decimal('0.00')
                )
                
                # Add 1-5 items to each invoice
                total = Decimal('0.00')
                for _ in range(random.randint(1, 5)):
                    product = random.choice(products)
                    quantity = random.randint(1, 5)
                    unit_price = product.price
                    subtotal = unit_price * quantity
                    total += subtotal
                
                invoice.total = total
                invoice.save()
        
        self.stdout.write(self.style.SUCCESS('✅ Sample data created successfully!'))
        self.stdout.write(f'Customers: {Customer.objects.count()}')
        self.stdout.write(f'Suppliers: {Supplier.objects.count()}')
        self.stdout.write(f'Products: {Product.objects.count()}')
        self.stdout.write(f'Sale Invoices: {SaleInvoice.objects.count()}')
        self.stdout.write(f'Purchase Orders: {PurchaseOrder.objects.count()}')
