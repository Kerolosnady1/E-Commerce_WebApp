#!/usr/bin/env python
"""
اختبار صفحة المخزون الرئيسية والجداول
Test main inventory page and table
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from core.models import InventoryItem
from django.test import Client
from django.urls import reverse

def test_inventory_page():
    """اختبار صفحة المخزون الرئيسية"""
    
    print("\n" + "="*60)
    print("🧪 اختبار صفحة المخزون الرئيسية")
    print("="*60 + "\n")
    
    items = InventoryItem.objects.all()
    if items.count() == 0:
        print("❌ لا توجد مخزونات!")
        return
    
    client = Client()
    response = client.get(reverse('inventory'))
    content = response.content.decode('utf-8')
    
    print(f"1️⃣  صفحة المخزون:")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ الصفحة تحمل بنجاح")
    
    print(f"\n2️⃣  البيانات المعروضة:")
    for item in items[:3]:
        if item.product.name in content:
            print(f"   ✅ المنتج: {item.product.name}")
        if str(item.quantity) in content:
            print(f"   ✅ الكمية: {item.quantity}")
        if str(item.reorder_level) in content:
            print(f"   ✅ حد إعادة الطلب: {item.reorder_level}")
    
    print(f"\n3️⃣  الأزرار والعناصر:")
    if 'tune' in content or 'إجراءات' in content:
        print("   ✅ أيقونة التحديث موجودة")
    if 'edit' in content:
        print("   ✅ أيقونة التعديل موجودة")
    
    print(f"\n4️⃣  الروابط:")
    item = items.first()
    update_link = f"/inventory/{item.id}/update/"
    if update_link in content:
        print(f"   ✅ رابط التحديث موجود: {update_link}")
    else:
        print(f"   ⚠️  رابط التحديث قد لا يكون موجوداً")
    
    print(f"\n5️⃣  الجداول والإحصائيات:")
    if 'إدارة المخزون' in content or 'المخزون' in content:
        print("   ✅ العنوان موجود")
    if 'البحث' in content or 'search' in content:
        print("   ✅ حقل البحث موجود")
    if 'الفلاتر' in content or 'filter' in content:
        print("   ✅ الفلاتر موجودة")
    
    print("\n" + "="*60)
    print("✅ انتهى الاختبار")
    print("="*60 + "\n")

if __name__ == '__main__':
    test_inventory_page()
