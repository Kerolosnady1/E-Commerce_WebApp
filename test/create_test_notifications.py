#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from core.models import Notification

# Create test notifications
notifications_data = [
    {
        "title": "طلب مبيعات جديد",
        "message": "تم استقبال طلب جديد من العميل أحمد محمد",
        "level": "info",
        "is_read": False
    },
    {
        "title": "تنبيه انخفاض المخزون",
        "message": "المنتج iPhone 15 انخفض إلى أقل من الحد الأدنى",
        "level": "warning",
        "is_read": False
    },
    {
        "title": "فاتورة تم دفعها",
        "message": "تم دفع الفاتورة #1005 بنجاح",
        "level": "success",
        "is_read": False
    },
    {
        "title": "خطأ في النظام",
        "message": "حدث خطأ في معالجة الدفع للفاتورة #1006",
        "level": "error",
        "is_read": False
    },
    {
        "title": "تقرير شهري متاح",
        "message": "التقرير المالي لشهر يناير متاح الآن",
        "level": "info",
        "is_read": True
    },
    {
        "title": "منتج جديد تم إضافته",
        "message": "تم إضافة منتج جديد: Samsung Galaxy S24",
        "level": "info",
        "is_read": True
    },
    {
        "title": "تحديث نظام",
        "message": "يوجد تحديث جديد للنظام متاح",
        "level": "warning",
        "is_read": True
    },
]

for data in notifications_data:
    Notification.objects.create(**data)

print(f"تم إنشاء {len(notifications_data)} تنبيهات")
print(f"إجمالي التنبيهات: {Notification.objects.count()}")
