import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from core.models import Customer
from decimal import Decimal

customers = Customer.objects.all()
print("Customer Balances:")
print("-" * 60)
total = Decimal('0')
for c in customers:
    print(f"{c.name}: {c.balance} ر.س")
    total += c.balance

print("-" * 60)
print(f"Total balance: {total} ر.س")
print(f"Number of customers: {customers.count()}")
