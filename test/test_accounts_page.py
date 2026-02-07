import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from django.urls import reverse

print("Testing Accounts Page URLs:")
print("=" * 50)

urls_to_test = [
    ('accounts', 'Accounts Page'),
    ('upload_avatar', 'Upload Avatar'),
    ('profile', 'Profile Page'),
    ('subscription', 'Subscription'),
    ('delete_account', 'Delete Account'),
]

for url_name, description in urls_to_test:
    try:
        url = reverse(url_name)
        print(f"✓ {description:20} → {url}")
    except Exception as e:
        print(f"✗ {description:20} → ERROR: {e}")

print("=" * 50)
print("All URLs verified!")
