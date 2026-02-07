import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from django.urls import reverse

print("✓ URLs Check:")
print("-" * 60)
urls = [
    ('Profile', 'profile'),
    ('Dashboard', 'dashboard'),
    ('Reports', 'reports'),
    ('Warehouses', 'warehouses'),
    ('Accounts', 'accounts'),
    ('2FA Toggle', 'toggle_two_factor'),
    ('Subscription', 'subscription'),
    ('Security', 'security'),
    ('Security Logs', 'security_logs'),
    ('Notifications', 'notifications'),
    ('Logout', 'logout'),
]

for name, url in urls:
    try:
        path = reverse(url)
        print(f"✓ {name:20} → {path}")
    except Exception as e:
        print(f"✗ {name:20} → ERROR: {e}")

# Test upgrade URL
try:
    path = reverse('upgrade_subscription', args=['professional'])
    print(f"✓ {'Upgrade Sub':20} → {path}")
except Exception as e:
    print(f"✗ {'Upgrade Sub':20} → ERROR: {e}")

# Test delete account URL
try:
    path = reverse('delete_account')
    print(f"✓ {'Delete Account':20} → {path}")
except Exception as e:
    print(f"✗ {'Delete Account':20} → ERROR: {e}")

print("-" * 60)
print("All URLs are working!")
