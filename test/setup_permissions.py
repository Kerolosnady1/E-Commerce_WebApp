import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from django.contrib.auth.models import Group
from core.models import Module, RolePermission

# Create modules
MODULES = [
    {
        'name_ar': 'المخزون والمنتجات',
        'name_en': 'Inventory & Products',
        'description_ar': 'إدارة الأصناف، المستودعات والتحويلات',
        'description_en': 'Manage products, warehouses and transfers',
        'icon': 'inventory_2',
        'color': 'blue',
        'order': 1,
    },
    {
        'name_ar': 'طلبات المبيعات',
        'name_en': 'Sales Orders',
        'description_ar': 'إنشاء الفواتير وعروض الأسعار',
        'description_en': 'Create invoices and quotes',
        'icon': 'shopping_cart',
        'color': 'green',
        'order': 2,
    },
    {
        'name_ar': 'إدارة العملاء (CRM)',
        'name_en': 'Customer Management (CRM)',
        'description_ar': 'بيانات العملاء وتاريخ المبيعات',
        'description_en': 'Customer data and sales history',
        'icon': 'group',
        'color': 'purple',
        'order': 3,
    },
    {
        'name_ar': 'التقارير المالية',
        'name_en': 'Financial Reports',
        'description_ar': 'تقارير الأرباح والخسائر والمبيعات',
        'description_en': 'P&L and sales reports',
        'icon': 'bar_chart',
        'color': 'orange',
        'order': 4,
    },
]

print("Creating modules...")
for m in MODULES:
    mod, created = Module.objects.get_or_create(
        name_ar=m['name_ar'],
        defaults={k: v for k, v in m.items() if k != 'name_ar'}
    )
    print(f"{'Created' if created else 'Exists'}: {m['name_ar']}")

# Get Sales group
try:
    sales_group = Group.objects.get(name='قسم المبيعات')
    print(f"\nFound group: {sales_group.name}")
    
    # Create permissions for sales
    PERMS = {
        'المخزون والمنتجات': ['view', 'export'],
        'طلبات المبيعات': ['view', 'add', 'change', 'export'],
        'إدارة العملاء (CRM)': ['view', 'add', 'change', 'export'],
        'التقارير المالية': ['view', 'export'],
    }
    
    print("\nCreating permissions for sales group...")
    for module_name, actions in PERMS.items():
        try:
            module = Module.objects.get(name_ar=module_name)
            for action in ['view', 'add', 'change', 'delete', 'export']:
                perm, created = RolePermission.objects.get_or_create(
                    group=sales_group,
                    module=module,
                    action=action,
                    defaults={'is_allowed': action in actions}
                )
                if created:
                    print(f"  Created: {action} for {module_name}")
        except Module.DoesNotExist:
            print(f"  Module not found: {module_name}")

except Group.DoesNotExist:
    print("Group 'قسم المبيعات' not found")

print("\nDone!")
