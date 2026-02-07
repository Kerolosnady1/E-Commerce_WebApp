#!/usr/bin/env python
"""
اختبار نموذج تحديث المخزون
Test inventory form functionality
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from core.models import InventoryItem, Product, Category
from core.forms import InventoryItemForm
from django.test import Client
from django.urls import reverse

def test_inventory_form():
    """اختبار الفورم والعروض"""
    
    print("\n" + "="*60)
    print("🧪 اختبار نموذج تحديث المخزون")
    print("="*60 + "\n")
    
    # 1. فحص البيانات الموجودة
    print("1️⃣  فحص المخزونات الموجودة:")
    items = InventoryItem.objects.all()
    if items.count() == 0:
        print("   ❌ لا توجد مخزونات! يجب إنشاء بيانات اختبار أولاً")
        return
    
    for item in items[:1]:
        print(f"   ✅ المنتج: {item.product.name}")
        print(f"      المعرف: {item.id}")
        print(f"      الكمية الحالية: {item.quantity}")
        print(f"      حد إعادة الطلب: {item.reorder_level}")
        
        # 2. اختبار الفورم
        print(f"\n2️⃣  اختبار الفورم:")
        form_data = {
            'quantity': 100,
            'reorder_level': 20,
        }
        form = InventoryItemForm(form_data, instance=item)
        if form.is_valid():
            print("   ✅ الفورم صحيح")
        else:
            print(f"   ❌ أخطاء الفورم: {form.errors}")
        
        # 3. اختبار الـ URL
        print(f"\n3️⃣  اختبار الـ URL والعروض:")
        client = Client()
        
        # اختبار GET
        url = reverse('inventory_update', args=[item.id])
        print(f"   URL: /inventory/{item.id}/update/")
        response = client.get(url)
        print(f"   GET Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ صفحة التحديث تحمل بنجاح")
        else:
            print(f"   ❌ خطأ في تحميل الصفحة")
        
        # اختبار POST
        print(f"\n4️⃣  اختبار تحديث البيانات:")
        response = client.post(url, {
            'quantity': 150,
            'reorder_level': 25,
        })
        if response.status_code == 302:  # Redirect
            print("   ✅ البيانات تم تحديثها بنجاح (تم إعادة التوجيه)")
            
            # فحص التحديث
            updated_item = InventoryItem.objects.get(id=item.id)
            if updated_item.quantity == 150 and updated_item.reorder_level == 25:
                print(f"   ✅ التحديث تم حفظه: الكمية = {updated_item.quantity}, الحد = {updated_item.reorder_level}")
            else:
                print(f"   ⚠️  البيانات لم تُحدّث كما هو متوقع")
        else:
            print(f"   ❌ فشل التحديث (Status: {response.status_code})")
    
    print("\n" + "="*60)
    print("✅ انتهى الاختبار")
    print("="*60 + "\n")

if __name__ == '__main__':
    test_inventory_form()
