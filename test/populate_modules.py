"""
Populate initial modules and role permissions to database
Run: python manage.py shell < populate_modules.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from django.contrib.auth.models import Group
from core.models import Module, RolePermission

# Define modules
MODULES_DATA = [
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
    {
        'name_ar': 'إدارة المستخدمين',
        'name_en': 'User Management',
        'description_ar': 'إنشاء وتعديل وحذف المستخدمين',
        'description_en': 'Create, update and delete users',
        'icon': 'people',
        'color': 'red',
        'order': 5,
    },
    {
        'name_ar': 'إعدادات النظام',
        'name_en': 'System Settings',
        'description_ar': 'إعدادات الشركة والنظام العام',
        'description_en': 'Company and system settings',
        'icon': 'settings',
        'color': 'gray',
        'order': 6,
    },
]

ACTIONS = ['view', 'add', 'change', 'delete', 'export']

# Get or create groups
GROUPS = {
    'مدير النظام': 'admin',
    'قسم المبيعات': 'sales',
    'المحاسب': 'accountant',
    'مدير المستودع': 'warehouse',
}

def create_modules():
    """Create modules"""
    print("Creating modules...")
    for module_data in MODULES_DATA:
        module, created = Module.objects.get_or_create(
            name_ar=module_data['name_ar'],
            defaults={
                'name_en': module_data['name_en'],
                'description_ar': module_data['description_ar'],
                'description_en': module_data['description_en'],
                'icon': module_data['icon'],
                'color': module_data['color'],
                'order': module_data['order'],
            }
        )
        if created:
            print(f"✓ Created module: {module.name_ar}")
        else:
            print(f"→ Module exists: {module.name_ar}")

def create_permissions():
    """Create permissions for all groups"""
    print("\nCreating permissions...")
    
    # Permission matrix for each role
    permission_matrix = {
        'مدير النظام': {  # Admin - All permissions
            'المخزون والمنتجات': ['view', 'add', 'change', 'delete', 'export'],
            'طلبات المبيعات': ['view', 'add', 'change', 'delete', 'export'],
            'إدارة العملاء (CRM)': ['view', 'add', 'change', 'delete', 'export'],
            'التقارير المالية': ['view', 'add', 'change', 'delete', 'export'],
            'إدارة المستخدمين': ['view', 'add', 'change', 'delete', 'export'],
            'إعدادات النظام': ['view', 'add', 'change', 'delete', 'export'],
        },
        'قسم المبيعات': {  # Sales
            'المخزون والمنتجات': ['view', 'export'],
            'طلبات المبيعات': ['view', 'add', 'change', 'export'],
            'إدارة العملاء (CRM)': ['view', 'add', 'change', 'export'],
            'التقارير المالية': ['view', 'export'],
            'إدارة المستخدمين': [],
            'إعدادات النظام': [],
        },
        'المحاسب': {  # Accountant
            'المخزون والمنتجات': ['view'],
            'طلبات المبيعات': ['view', 'export'],
            'إدارة العملاء (CRM)': ['view'],
            'التقارير المالية': ['view', 'add', 'change', 'export'],
            'إدارة المستخدمين': [],
            'إعدادات النظام': [],
        },
        'مدير المستودع': {  # Warehouse Manager
            'المخزون والمنتجات': ['view', 'add', 'change', 'export'],
            'طلبات المبيعات': ['view'],
            'إدارة العملاء (CRM)': [],
            'التقارير المالية': [],
            'إدارة المستخدمين': [],
            'إعدادات النظام': [],
        },
    }
    
    for group_name, modules_perms in permission_matrix.items():
        try:
            group = Group.objects.get(name=group_name)
            print(f"\n📋 Setting permissions for: {group_name}")
            
            for module_name, actions in modules_perms.items():
                try:
                    module = Module.objects.get(name_ar=module_name)
                    
                    # Create permission for each action
                    for action in ACTIONS:
                        perm, created = RolePermission.objects.get_or_create(
                            group=group,
                            module=module,
                            action=action,
                            defaults={'is_allowed': action in actions}
                        )
                        
                        # Update if exists
                        if not created and perm.is_allowed != (action in actions):
                            perm.is_allowed = action in actions
                            perm.save()
                        
                        status = "✓" if perm.is_allowed else "✗"
                        if created:
                            print(f"  {status} {module_name} - {action}")
                            
                except Module.DoesNotExist:
                    print(f"  ✗ Module not found: {module_name}")
        
        except Group.DoesNotExist:
            print(f"  ✗ Group not found: {group_name}")

if __name__ == '__main__':
    print("=" * 60)
    print("Populating Modules and Permissions...")
    print("=" * 60)
    
    create_modules()
    create_permissions()
    
    print("\n" + "=" * 60)
    print("✓ Done!")
    print("=" * 60)
