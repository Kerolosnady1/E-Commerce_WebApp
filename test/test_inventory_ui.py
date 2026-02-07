#!/usr/bin/env python
"""
اختبار زر الإلغاء وسير العمل الكامل
Test cancel button and full workflow
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from core.models import InventoryItem
from django.test import Client
from django.urls import reverse

def test_cancel_button():
    """اختبار زر الإلغاء والعودة للصفحة الرئيسية"""
    
    print("\n" + "="*60)
    print("🧪 اختبار زر الإلغاء والعودة")
    print("="*60 + "\n")
    
    items = InventoryItem.objects.all()
    if items.count() == 0:
        print("❌ لا توجد مخزونات!")
        return
    
    item = items.first()
    client = Client()
    
    # 1. اختبار الوصول للصفحة الرئيسية للمخزون
    print("1️⃣  اختبار الوصول لصفحة المخزون الرئيسية:")
    response = client.get(reverse('inventory'))
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ صفحة المخزون تحمل بنجاح")
    else:
        print(f"   ❌ خطأ في تحميل الصفحة")
    
    # 2. اختبار الوصول لصفحة التحديث
    print(f"\n2️⃣  اختبار الوصول لصفحة تحديث المخزون:")
    update_url = reverse('inventory_update', args=[item.id])
    response = client.get(update_url)
    print(f"   URL: {update_url}")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ صفحة التحديث تحمل بنجاح")
        
        # فحص المحتوى
        content = response.content.decode('utf-8')
        if 'تحديث المخزون' in content:
            print("   ✅ عنوان الصفحة صحيح")
        if f'المنتج: {item.product.name}' in content or item.product.name in content:
            print(f"   ✅ اسم المنتج معروض: {item.product.name}")
        if f'value="{item.quantity}"' in content or f'value="{str(item.quantity)}"' in content:
            print(f"   ✅ الكمية الحالية معروضة: {item.quantity}")
        if f'value="{item.reorder_level}"' in content or f'value="{str(item.reorder_level)}"' in content:
            print(f"   ✅ حد إعادة الطلب معروض: {item.reorder_level}")
        if 'تحديث' in content and 'إلغاء' in content:
            print("   ✅ الزران موجودة (تحديث و إلغاء)")
    
    # 3. اختبار الرابط في HTML template
    print(f"\n3️⃣  فحص HTML للصفحة:")
    inventory_url = reverse('inventory')
    if f'href="{inventory_url}"' in content or 'href="{% url' in content:
        print("   ✅ رابط الإلغاء يشير إلى صفحة المخزون")
    
    # 4. اختبار النموذج والأزرار
    print(f"\n4️⃣  اختبار العناصر في HTML:")
    if '<form method="post"' in content:
        print("   ✅ نموذج POST موجود")
    if 'type="submit"' in content:
        print("   ✅ زر التحديث موجود")
    if 'type="number"' in content:
        print("   ✅ حقول الأرقام موجودة")
    if 'name="quantity"' in content:
        print("   ✅ حقل الكمية موجود")
    if 'name="reorder_level"' in content:
        print("   ✅ حقل حد إعادة الطلب موجود")
    
    print("\n" + "="*60)
    print("✅ انتهى الاختبار")
    print("="*60 + "\n")

if __name__ == '__main__':
    test_cancel_button()
