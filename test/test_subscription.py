import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from core.models import UserProfile, Subscription
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

# Test creating a subscription for the first user
try:
    user = User.objects.first()
    if user:
        sub, created = Subscription.objects.get_or_create(
            user=user,
            defaults={
                'plan': 'professional',
                'renewal_date': timezone.now().date() + timedelta(days=30),
                'monthly_cost': 149.00,
                'storage_total': 100.00
            }
        )
        print(f"User: {user.username}")
        print(f"Subscription created: {created}")
        print(f"Plan: {sub.get_plan_display()}")
        print(f"Monthly Cost: {sub.monthly_cost} ر.س")
        print(f"Storage: {sub.storage_used}/{sub.storage_total} GB")
        print(f"Storage %: {sub.storage_percent()}%")
    else:
        print("No users found")
except Exception as e:
    print(f"Error: {e}")
