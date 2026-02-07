#!/usr/bin/env python
"""
اختبار البحث على جميع الصفحات
Test search functionality across all pages
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from core.models import Product, Supplier, PurchaseOrder, SaleInvoice

def test_search():
    """اختبار البحث على جميع الصفحات"""
    
    print("\n" + "="*70)
    print("🧪 اختبار البحث على جميع الصفحات")
    print("="*70 + "\n")
    
    client = Client()
    
    # 1. اختبار البحث في المخزون
    print("1️⃣  البحث في المخزون:")
    response = client.get(reverse('inventory') + '?search=samsung')
    if response.status_code == 200:
        print(f"   ✅ البحث يعمل (Status 200)")
        if 'samsung' in response.content.decode('utf-8').lower() or 'Samsung' in response.content.decode('utf-8'):
            print(f"   ✅ النتائج تحتوي على المصطلح المبحوث")
        else:
            print(f"   ⚠️  قد لا تحتوي النتائج على المصطلح المبحوث")
    else:
        print(f"   ❌ خطأ: Status {response.status_code}")
    
    # 2. اختبار البحث العام (AJAX)
    print("\n2️⃣  البحث العام (AJAX):")
    response = client.get(reverse('search') + '?q=test', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    if response.status_code == 200:
        print(f"   ✅ البحث يعمل (Status 200)")
        data = response.json()
        print(f"   📊 النتائج: {len(data.get('customers', []))} عملاء، {len(data.get('products', []))} منتجات")
    else:
        print(f"   ❌ خطأ: Status {response.status_code}")
    
    # 3. اختبار البحث في المشتريات
    print("\n3️⃣  البحث في المشتريات:")
    response = client.get(reverse('purchase_search') + '?q=test', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    if response.status_code == 200:
        print(f"   ✅ البحث يعمل (Status 200)")
        data = response.json()
        print(f"   📊 عدد النتائج: {len(data.get('results', []))}")
    else:
        print(f"   ❌ خطأ: Status {response.status_code}")
    
    # 4. اختبار البحث في المبيعات
    print("\n4️⃣  البحث في المبيعات:")
    response = client.get(reverse('sales') + '?search=test')
    if response.status_code == 200:
        print(f"   ✅ البحث يعمل (Status 200)")
    else:
        print(f"   ❌ خطأ: Status {response.status_code}")
    
    # 5. اختبار البحث في التقارير
    print("\n5️⃣  البحث في التقارير:")
    response = client.get(reverse('reports') + '?search=test')
    if response.status_code == 200:
        print(f"   ✅ البحث يعمل (Status 200)")
    else:
        print(f"   ❌ خطأ: Status {response.status_code}")
    
    # 6. اختبار البحث في العملاء
    print("\n6️⃣  البحث في العملاء:")
    response = client.get(reverse('customers') + '?search=test')
    if response.status_code == 200:
        print(f"   ✅ البحث يعمل (Status 200)")
    else:
        print(f"   ❌ خطأ: Status {response.status_code}")
    
    print("\n" + "="*70)
    print("✅ انتهى الاختبار")
    print("="*70 + "\n")

if __name__ == '__main__':
    test_search()
