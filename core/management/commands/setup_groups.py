from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from core.models import (
    Category, Customer, InventoryItem, Notification, Product,
    PurchaseOrder, SaleInvoice, SaleItem, Supplier, TaxRate, UserProfile
)


class Command(BaseCommand):
    help = 'Create user groups with appropriate permissions for the ERP system'

    def handle(self, *args, **options):
        # Define groups and their permissions
        groups_config = {
            'مدير النظام': {
                'display_name': 'System Manager',
                'models': [
                    (Category, ['add', 'change', 'delete', 'view']),
                    (Customer, ['add', 'change', 'delete', 'view']),
                    (Product, ['add', 'change', 'delete', 'view']),
                    (InventoryItem, ['add', 'change', 'delete', 'view']),
                    (SaleInvoice, ['add', 'change', 'delete', 'view']),
                    (SaleItem, ['add', 'change', 'delete', 'view']),
                    (PurchaseOrder, ['add', 'change', 'delete', 'view']),
                    (Supplier, ['add', 'change', 'delete', 'view']),
                    (TaxRate, ['add', 'change', 'delete', 'view']),
                    (Notification, ['add', 'change', 'delete', 'view']),
                    (UserProfile, ['add', 'change', 'delete', 'view']),
                ]
            },
            'المحاسب': {
                'display_name': 'Accountant',
                'models': [
                    (SaleInvoice, ['view', 'change']),
                    (Customer, ['view', 'change']),
                    (PurchaseOrder, ['view']),
                    (TaxRate, ['view']),
                    (Notification, ['view']),
                ]
            },
            'مدير المستودع': {
                'display_name': 'Warehouse Manager',
                'models': [
                    (InventoryItem, ['view', 'change']),
                    (Product, ['view', 'change']),
                    (PurchaseOrder, ['view', 'change']),
                    (SaleInvoice, ['view']),
                    (Supplier, ['view']),
                    (Category, ['view']),
                ]
            },
            'قسم المبيعات': {
                'display_name': 'Sales Department',
                'models': [
                    (SaleInvoice, ['add', 'view', 'change']),
                    (SaleItem, ['add', 'view']),
                    (Customer, ['view', 'add', 'change']),
                    (Product, ['view']),
                    (InventoryItem, ['view']),
                    (Notification, ['view']),
                ]
            },
        }

        # Create groups with permissions
        for group_name, config in groups_config.items():
            group, created = Group.objects.get_or_create(name=group_name)
            
            # Clear existing permissions
            group.permissions.clear()
            
            # Add permissions for each model
            for model, actions in config['models']:
                content_type = ContentType.objects.get_for_model(model)
                
                for action in actions:
                    permission = Permission.objects.filter(
                        content_type=content_type,
                        codename__startswith=action
                    ).first()
                    
                    if permission:
                        group.permissions.add(permission)
            
            status = "Created" if created else "Updated"
            self.stdout.write(
                self.style.SUCCESS(
                    f'{status} group: {group_name} ({config["display_name"]}) with {group.permissions.count()} permissions'
                )
            )

        self.stdout.write(self.style.SUCCESS('Successfully set up user groups!'))
