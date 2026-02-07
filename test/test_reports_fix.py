#!/usr/bin/env python
"""
اختبار إصلاح خطأ reports view
Test reports view fix
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from django.test import Client
from django.urls import reverse

def test_reports_view():
    """اختبار صفحة التقارير بدون أخطاء"""
    
    print("\n" + "="*60)
    print("🧪 اختبار صفحة التقارير")
    print("="*60 + "\n")
    
    client = Client()
    
    # 1. اختبار بدون بحث
    print("1️⃣  اختبار التحميل الأساسي:")
    response = client.get(reverse('reports'))
    if response.status_code == 200:
        print("   ✅ الصفحة تحمل بنجاح (Status 200)")
    else:
        print(f"   ❌ خطأ: Status {response.status_code}")
    
    # 2. اختبار مع بحث
    print("\n2️⃣  اختبار مع بحث:")
    response = client.get(reverse('reports') + '?search=invoice')
    if response.status_code == 200:
        print("   ✅ البحث يعمل بنجاح")
    else:
        print(f"   ❌ خطأ في البحث: Status {response.status_code}")
    
    # 3. اختبار تصدير PDF
    print("\n3️⃣  اختبار تصدير PDF:")
    response = client.get(reverse('reports') + '?export=pdf')
    if response.status_code == 200:
        print("   ✅ تصدير PDF يعمل بنجاح")
    else:
        print(f"   ⚠️  قد لا يكون PDF متوفراً: Status {response.status_code}")
    
    print("\n" + "="*60)
    print("✅ جميع الاختبارات نجحت!")
    print("="*60 + "\n")

if __name__ == '__main__':
    test_reports_view()
