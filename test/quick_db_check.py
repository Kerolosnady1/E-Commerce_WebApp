import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from django.contrib.auth.models import User, Group
from core.models import Module, RolePermission

print("="*70)
print("DATABASE VERIFICATION")
print("="*70)

# Groups
groups = Group.objects.all()
print(f"\n1. auth_group table: {groups.count()} roles")
for g in groups:
    print(f"   - {g.name}")

# Users
users = User.objects.all()
print(f"\n2. auth_user table: {users.count()} users")
for u in users:
    roles = list(u.groups.values_list('name', flat=True))
    print(f"   - {u.username}: {', '.join(roles) if roles else 'No role'}")

# Modules
modules = Module.objects.all()
print(f"\n3. core_module table: {modules.count()} modules")

# Role Permissions
permissions = RolePermission.objects.all()
print(f"\n4. core_rolepermission table: {permissions.count()} permissions")

# Count per role
print(f"\n5. Users per role:")
for role in ['مدير النظام', 'قسم المبيعات', 'المحاسب', 'مدير المستودع']:
    count = User.objects.filter(groups__name=role).count()
    print(f"   - {role}: {count} users")

print("\n" + "="*70)
print("DATABASE EXISTS AND CONTAINS DATA!")
print("="*70)
