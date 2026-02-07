from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal
import json
import os
from django.core.files.storage import default_storage

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, Permission, User
from django.db.models import Count, F, Q, Sum
from django.db.models.deletion import ProtectedError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .middleware import get_client_ip

from .forms import (
    CategoryForm,
    CustomerForm,
    InventoryItemForm,
    NotificationForm,
    ProductForm,
    PurchaseOrderForm,
    SaleInvoiceForm,
    SupplierForm,
    TaxRateForm,
    UserRegistrationForm,
    WarehouseForm,
)
from .models import (
    Category,
    Customer,
    InventoryItem,
    Notification,
    Product,
    PurchaseOrder,
    SaleInvoice,
    SaleItem,
    Subscription,
    Supplier,
    TaxRate,
    CompanySettings,
    UserProfile,
    Warehouse,
    SecurityLog,
    PrintTemplate,
)

UI_TEMPLATES = {
    "dashboard": "00-Business_Insights_Dashboard_System_Code.html",
    "sales": "01-Sales_Management_System_Code.html",
    "customers": "02-Customer_Management_System_Code.html",
    "reports": "03-Reports_&_Analytics_System_Code.html",
    "general_settings": "04-General_Settings_System_Code.html",
    "accounts": "05-Account_Management_System_Code.html",
    "inventory": "06-Inventory_Management_System_Code.html",
    "purchases": "07-Purchases_Management_System_Code.html",
    "warehouses": "15-Warehouses_Management_System_Code.html",
    "taxes": "08-Tax_Management_System_Code.html",
    "print_templates": "print_templates.html",
    "notifications": "10-Notifications_Center_System_Code.html",
    "security": "11-Security_&_Permissions_System_Code.html",
    "locale_time": "12-Language_&_Time_System_Code.html",
    "users_permissions": "13-Users_&_Permissions_System_Code.html",
    "system_settings": "14-General_Settings_System_Code.html",
}


def dashboard(request):
    """Dashboard with real-time statistics and analytics"""
    # Get date ranges
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Sales statistics
    total_sales = SaleInvoice.objects.filter(status='paid').aggregate(
        total=Sum('total')
    )['total'] or Decimal('0')
    
    sales_this_month = SaleInvoice.objects.filter(
        issued_date__gte=month_ago,
        status='paid'
    ).aggregate(total=Sum('total'))['total'] or Decimal('0')
    
    sales_this_week = SaleInvoice.objects.filter(
        issued_date__gte=week_ago,
        status='paid'
    ).aggregate(total=Sum('total'))['total'] or Decimal('0')
    
    # Customer statistics
    total_customers = Customer.objects.filter(is_active=True).count()
    new_customers_this_month = Customer.objects.filter(
        created_at__gte=month_ago
    ).count()
    
    # Inventory statistics
    total_products = Product.objects.filter(is_active=True).count()
    low_stock_items = InventoryItem.objects.filter(
        quantity__lte=F('reorder_level')
    ).count()
    
    # Invoice statistics
    total_invoices = SaleInvoice.objects.count()
    paid_invoices = SaleInvoice.objects.filter(status=SaleInvoice.STATUS_PAID).count()

    # Recent invoices
    recent_invoices = SaleInvoice.objects.select_related('customer').order_by('-created_at')[:10]
    
    # Recent notifications
    recent_notifications = Notification.objects.filter(is_read=False).order_by('-created_at')[:5]
    
    # Purchase orders pending
    pending_purchases = PurchaseOrder.objects.filter(status='pending').count()

    # Low stock details
    low_stock_list = (
        InventoryItem.objects.filter(quantity__lte=F('reorder_level'))
        .select_related('product', 'product__category')
        .order_by('quantity')[:10]
    )
    
    # Monthly sales data for chart (last 12 months)
    from django.db.models.functions import TruncMonth
    start_month = today.replace(day=1)
    start_year = start_month.year
    start_month_num = start_month.month - 11
    while start_month_num <= 0:
        start_month_num += 12
        start_year -= 1
    start_date = date(start_year, start_month_num, 1)

    monthly_sales = (
        SaleInvoice.objects.filter(status='paid')
        .filter(issued_date__gte=start_date)
        .annotate(month=TruncMonth('issued_date'))
        .values('month')
        .annotate(total=Sum('total'))
        .order_by('month')
    )
    
    # Build monthly data with Arabic month names
    arabic_months = [
        'يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو',
        'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'
    ]
    
    monthly_data = []
    max_sales = Decimal('0')
    
    for entry in monthly_sales:
        total = entry['total'] or Decimal('0')
        if total > max_sales:
            max_sales = total
        month_value = entry.get('month')
        month_num = month_value.month if month_value else 0
        monthly_data.append({
            'month_name': arabic_months[month_num - 1] if 1 <= month_num <= 12 else 'غير معروف',
            'total': float(total),
            'month_num': month_num
        })
    
    # Calculate percentages for bar heights (0-100%)
    max_sales_float = float(max_sales) if max_sales > 0 else 1
    for item in monthly_data:
        item['height'] = (item['total'] / max_sales_float) * 100 if max_sales_float > 0 else 0
    
    context = {
        'total_sales': total_sales,
        'sales_this_month': sales_this_month,
        'sales_this_week': sales_this_week,
        'total_customers': total_customers,
        'new_customers_this_month': new_customers_this_month,
        'total_products': total_products,
        'low_stock_items': low_stock_items,
        'total_invoices': total_invoices,
        'paid_invoices': paid_invoices,
        'recent_invoices': recent_invoices,
        'recent_notifications': recent_notifications,
        'pending_purchases': pending_purchases,
        'low_stock_list': low_stock_list,
        'monthly_sales': monthly_data,
    }
    
    return render(request, UI_TEMPLATES["dashboard"], context)


def sales(request):
    """Sales management with invoice listing, search, and filtering"""
    # Get filter and search parameters
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    page = int(request.GET.get('page', 1))
    per_page = 15
    
    # Start with all invoices
    invoices = SaleInvoice.objects.select_related('customer').order_by('-issued_date')
    
    # Apply status filter
    if status_filter in ['paid', 'pending', 'overdue']:
        invoices = invoices.filter(status=status_filter)
    
    # Apply search query
    if search_query:
        invoices = invoices.filter(
            Q(number__icontains=search_query) | 
            Q(customer__name__icontains=search_query)
        )
    
    # Apply date range filter
    if date_from:
        invoices = invoices.filter(issued_date__gte=date_from)
    if date_to:
        invoices = invoices.filter(issued_date__lte=date_to)
    
    # Get total count for pagination
    total_count = invoices.count()
    total_pages = (total_count + per_page - 1) // per_page
    
    # Calculate offset and slice
    offset = (page - 1) * per_page
    invoices_page = invoices[offset:offset + per_page]
    
    # Statistics on full queryset (before pagination)
    all_invoices_for_stats = SaleInvoice.objects.select_related('customer')
    sales_this_month = all_invoices_for_stats.filter(status='paid').aggregate(
        total=Sum('total')
    )['total'] or Decimal('0')
    
    total_sales = all_invoices_for_stats.aggregate(total=Sum('total'))['total'] or Decimal('0')
    pending_invoices = all_invoices_for_stats.filter(status='pending').count()
    paid_invoices = all_invoices_for_stats.filter(status='paid').count()
    
    context = {
        'invoices': invoices_page,
        'total_sales': total_sales,
        'sales_this_month': sales_this_month,
        'pending_invoices': pending_invoices,
        'paid_invoices': paid_invoices,
        'total_count': total_count,
        'total_pages': total_pages,
        'current_page': page,
        'status_filter': status_filter,
        'search_query': search_query,
        'date_from': date_from,
        'date_to': date_to,
        'per_page': per_page,
    }
    
    return render(request, UI_TEMPLATES["sales"], context)


def customers(request):
    """Customer management with CRUD operations"""
    today = timezone.now().date()
    month_ago = today - timedelta(days=30)
    
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="customers.csv"'
        response.write('\ufeff')
        response.write('name,email,phone,balance,is_active,created_at\n')
        for customer in Customer.objects.all().order_by('-created_at'):
            response.write(
                f"{customer.name},{customer.email},{customer.phone},{customer.balance},{customer.is_active},{customer.created_at}\n"
            )
        return response
    
    # Get search query
    search_query = request.GET.get('search', '').strip()
    
    customers_list = Customer.objects.annotate(
        total_orders=Count('invoices')
    ).order_by('-created_at')
    
    # Apply search filter
    if search_query:
        customers_list = customers_list.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    # Statistics (on full dataset before search)
    all_customers = Customer.objects.all()
    total_customers = all_customers.count()
    active_customers = all_customers.filter(is_active=True).count()
    new_customers_this_month = all_customers.filter(created_at__gte=month_ago).count()
    total_balance = all_customers.aggregate(total=Sum('balance'))['total'] or Decimal('0')
    
    context = {
        'customers': customers_list,
        'total_customers': total_customers,
        'active_customers': active_customers,
        'new_customers_this_month': new_customers_this_month,
        'total_balance': total_balance,
        'search_query': search_query,  # ✅ إضافة search_query للسياق
    }
    
    return render(request, UI_TEMPLATES["customers"], context)


def reports(request):
    """Reports and analytics with filtering options"""
    from datetime import datetime, timedelta
    from django.db.models import Sum, Count, Avg
    
    # Get filter parameters
    quarter = request.GET.get('quarter', 'current')
    category_filter = request.GET.get('category', 'all')
    report_type = request.GET.get('report_type', 'financial')  # financial, sales, inventory, expenses
    search_query = request.GET.get('search', '').strip()
    
    # Date ranges based on quarter
    today = timezone.now().date()
    if quarter == 'current':
        start_date = today.replace(day=1)
        end_date = today
    elif quarter == 'q1':
        start_date = today.replace(month=1, day=1)
        end_date = today.replace(month=3, day=31)
    elif quarter == 'q2':
        start_date = today.replace(month=4, day=1)
        end_date = today.replace(month=6, day=30)
    elif quarter == 'q3':
        start_date = today.replace(month=7, day=1)
        end_date = today.replace(month=9, day=30)
    elif quarter == 'q4':
        start_date = today.replace(month=10, day=1)
        end_date = today.replace(month=12, day=31)
    else:
        start_date = today - timedelta(days=30)
        end_date = today
    
    # Calculate revenue (from sales invoices)
    invoices = SaleInvoice.objects.filter(
        issued_date__gte=start_date,
        issued_date__lte=end_date
    )
    
    # Apply search filter to invoices
    if search_query:
        invoices = invoices.filter(
            Q(number__icontains=search_query) |
            Q(customer__name__icontains=search_query)
        )
    
    if category_filter != 'all':
        invoices = invoices.filter(status=category_filter)
    
    total_revenue = invoices.filter(status='paid').aggregate(Sum('total'))['total__sum'] or 0
    previous_month_revenue = SaleInvoice.objects.filter(
        issued_date__gte=start_date - timedelta(days=30),
        issued_date__lt=start_date,
        status='paid'
    ).aggregate(Sum('total'))['total__sum'] or 1
    
    revenue_change = ((total_revenue - previous_month_revenue) / previous_month_revenue * 100) if previous_month_revenue else 0
    
    # Calculate expenses (estimated from purchase orders)
    total_expenses = PurchaseOrder.objects.filter(
        issued_date__gte=start_date,
        issued_date__lte=end_date
    ).aggregate(Sum('total'))['total__sum'] or 0
    
    previous_month_expenses = PurchaseOrder.objects.filter(
        issued_date__gte=start_date - timedelta(days=30),
        issued_date__lt=start_date
    ).aggregate(Sum('total'))['total__sum'] or 1
    
    expenses_change = ((total_expenses - previous_month_expenses) / previous_month_expenses * 100) if previous_month_expenses else 0
    
    # Calculate profit
    net_profit = total_revenue - total_expenses
    previous_profit = previous_month_revenue - previous_month_expenses
    profit_change = ((net_profit - previous_profit) / previous_profit * 100) if previous_profit else 0
    
    # Profit margin
    profit_margin = (net_profit / total_revenue * 100) if total_revenue else 0
    
    # Recent transactions
    recent_transactions = SaleInvoice.objects.select_related('customer').order_by('-created_at')
    
    # Apply search filter to recent transactions
    if search_query:
        recent_transactions = recent_transactions.filter(
            Q(number__icontains=search_query) |
            Q(customer__name__icontains=search_query)
        )
    
    # Now apply the slice after filtering
    recent_transactions = recent_transactions[:10]
    
    # Monthly revenue data for chart (last 7 months)
    monthly_data = []
    for i in range(6, -1, -1):
        month_start = (today.replace(day=1) - timedelta(days=i*30)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        month_revenue = SaleInvoice.objects.filter(
            issued_date__gte=month_start,
            issued_date__lte=month_end,
            status='paid'
        ).aggregate(Sum('total'))['total__sum'] or 0
        monthly_data.append({
            'month': month_start.strftime('%B'),
            'revenue': float(month_revenue)
        })
    
    # Handle export
    if request.GET.get('export') == 'pdf':
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="financial_report.pdf"'
            
            doc = SimpleDocTemplate(response, pagesize=A4)
            story = []
            styles = getSampleStyleSheet()
            
            story.append(Paragraph("تقرير المبيعات المالي", styles['Title']))
            story.append(Spacer(1, 12))
            story.append(Paragraph(f"إجمالي الإيرادات: ${total_revenue:,.2f}", styles['Normal']))
            story.append(Paragraph(f"إجمالي المصاريف: ${total_expenses:,.2f}", styles['Normal']))
            story.append(Paragraph(f"صافي الربح: ${net_profit:,.2f}", styles['Normal']))
            
            doc.build(story)
            return response
        except ImportError:
            # reportlab not installed, fallback to CSV
            messages.warning(request, 'PDF export not available. Exporting as CSV instead.')
            request.GET = request.GET.copy()
            request.GET['export'] = 'csv'
    
    if request.GET.get('export') == 'csv':
        import csv
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="financial_report.csv"'
        response.write('\ufeff')
        
        writer = csv.writer(response)
        writer.writerow(['رقم الفاتورة', 'العميل', 'التاريخ', 'المبلغ', 'الحالة'])
        for invoice in invoices:
            writer.writerow([
                invoice.number,
                invoice.customer.name,
                invoice.issued_date.strftime('%Y-%m-%d'),
                f'${invoice.total}',
                invoice.get_status_display()
            ])
        return response
    
    # Convert monthly_data to JSON for JavaScript
    import json
    monthly_data_json = json.dumps(monthly_data)
    
    context = {
        'total_revenue': total_revenue,
        'revenue_change': revenue_change,
        'total_expenses': total_expenses,
        'expenses_change': expenses_change,
        'net_profit': net_profit,
        'profit_change': profit_change,
        'profit_margin': profit_margin,
        'recent_transactions': recent_transactions,
        'monthly_data': monthly_data_json,
        'quarter': quarter,
        'category_filter': category_filter,
        'report_type': report_type,
        'search_query': search_query,
    }
    return render(request, UI_TEMPLATES["reports"], context)


def general_settings(request):
    settings_obj, _ = CompanySettings.objects.get_or_create(id=1)

    if request.method == 'POST':
        if request.POST.get('action') == 'remove_logo':
            if settings_obj.logo:
                settings_obj.logo.delete(save=False)
            settings_obj.logo = None
            settings_obj.save(update_fields=['logo'])
            messages.success(request, 'تم إزالة شعار الشركة')
            return redirect('general_settings')

        settings_obj.company_name_ar = request.POST.get('company_name_ar', '')
        settings_obj.company_name_en = request.POST.get('company_name_en', '')
        settings_obj.currency = request.POST.get('currency', settings_obj.currency)
        settings_obj.timezone = request.POST.get('timezone', settings_obj.timezone)

        settings_obj.tax_enabled = request.POST.get('tax_enabled') == 'on'
        settings_obj.vat_number = request.POST.get('vat_number', '')
        default_tax_rate = request.POST.get('default_tax_rate')
        if default_tax_rate:
            try:
                settings_obj.default_tax_rate = Decimal(default_tax_rate)
            except Exception:
                settings_obj.default_tax_rate = settings_obj.default_tax_rate
        settings_obj.prices_include_tax = request.POST.get('prices_include_tax') == 'on'
        settings_obj.show_vat_on_invoice = request.POST.get('show_vat_on_invoice') == 'on'

        if 'logo' in request.FILES:
            settings_obj.logo = request.FILES['logo']

        settings_obj.save()

        # Sync default tax rate record
        tax_rate_value = settings_obj.default_tax_rate
        tax_rate, _ = TaxRate.objects.get_or_create(
            name='ضريبة القيمة المضافة',
            defaults={
                'rate': tax_rate_value,
                'is_default': True,
            },
        )
        tax_rate.rate = tax_rate_value
        tax_rate.is_default = True
        tax_rate.save()

        messages.success(request, 'تم حفظ إعدادات الشركة بنجاح')
        return redirect('general_settings')

    currency_options = [
        ('SAR', 'ريال سعودي (SAR)'),
        ('AED', 'درهم إماراتي (AED)'),
        ('USD', 'دولار أمريكي (USD)'),
        ('KWD', 'دينار كويتي (KWD)'),
        ('QAR', 'ريال قطري (QAR)'),
    ]

    timezone_options = [
        ('Asia/Riyadh', '(GMT+03:00) الرياض'),
        ('Asia/Dubai', '(GMT+04:00) دبي'),
        ('Africa/Cairo', '(GMT+02:00) القاهرة'),
        ('Europe/London', '(GMT+00:00) لندن'),
    ]

    context = {
        'settings_obj': settings_obj,
        'currency_options': currency_options,
        'timezone_options': timezone_options,
    }

    return render(request, UI_TEMPLATES["general_settings"], context)


def system_settings(request):
    import os
    from django.conf import settings as django_settings
    
    settings_obj = CompanySettings.objects.first()
    if not settings_obj:
        settings_obj = CompanySettings.objects.create()
    
    # Calculate actual storage usage from media files
    storage_used_mb = 0
    media_root = django_settings.MEDIA_ROOT
    
    if os.path.exists(media_root):
        for dirpath, dirnames, filenames in os.walk(media_root):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    storage_used_mb += os.path.getsize(filepath)
        
        # Convert bytes to MB
        storage_used_mb = storage_used_mb / (1024 * 1024)
    
    # Update storage in database
    settings_obj.storage_used_mb = round(storage_used_mb, 2)
    settings_obj.save(update_fields=['storage_used_mb'])
    
    # Calculate storage percentage
    storage_quota_mb = settings_obj.storage_quota_mb
    storage_percentage = min(100, (storage_used_mb / storage_quota_mb * 100)) if storage_quota_mb > 0 else 0
    
    # Convert to GB for display
    storage_used_gb = storage_used_mb / 1024
    storage_quota_gb = storage_quota_mb / 1024

    context = {
        'company_name_ar': settings_obj.company_name_ar,
        'company_name_en': settings_obj.company_name_en,
        'vat_number': settings_obj.vat_number,
        'company_logo_url': settings_obj.logo.url if settings_obj.logo else '',
        'company_logo_default': settings_obj.logo.url if settings_obj.logo else '',
        'currency': settings_obj.currency,
        'tax_enabled': settings_obj.tax_enabled,
        'default_tax_rate': settings_obj.default_tax_rate,
        'prices_include_tax': settings_obj.prices_include_tax,
        'show_vat_on_invoice': settings_obj.show_vat_on_invoice,
        'default_print_template': settings_obj.default_print_template,
        'storage_used_mb': round(storage_used_mb, 2),
        'storage_quota_mb': storage_quota_mb,
        'storage_used_gb': round(storage_used_gb, 2),
        'storage_quota_gb': round(storage_quota_gb, 2),
        'storage_percentage': round(storage_percentage, 1),
    }

    return render(request, UI_TEMPLATES["system_settings"], context)


@login_required(login_url='login')
def accounts(request):
    """Account management with financial overview and profile editing"""
    # Force evaluation of lazy user object by accessing its ID
    user_id = request.user.id
    
    if request.method == 'POST':
        # Handle profile update
        if 'update_profile' in request.POST:
            user = request.user
            user.first_name = request.POST.get('first_name', '')
            user.last_name = request.POST.get('last_name', '')
            user.email = request.POST.get('email', '')
            user.save()
            
            # Update profile fields
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.phone = request.POST.get('phone', '')
            profile.save()
            
            messages.success(request, 'تم تحديث الملف الشخصي بنجاح')
            return redirect('accounts')
        
        # Handle password change
        elif 'change_password' in request.POST:
            current_password = request.POST.get('current_password', '')
            new_password = request.POST.get('new_password', '')
            confirm_password = request.POST.get('confirm_password', '')
            
            user = request.user
            if not user.check_password(current_password):
                messages.error(request, 'كلمة المرور الحالية غير صحيحة')
            elif new_password != confirm_password:
                messages.error(request, 'كلمات المرور الجديدة غير متطابقة')
            elif len(new_password) < 8:
                messages.error(request, 'يجب أن تكون كلمة المرور 8 أحرف على الأقل')
            else:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'تم تغيير كلمة المرور بنجاح')
                return redirect('accounts')
    
    # Get user profile and subscription
    profile, created = UserProfile.objects.get_or_create(user_id=user_id)
    subscription, created = Subscription.objects.get_or_create(user_id=user_id)
    
    # Get all invoices for accounting
    paid_invoices = SaleInvoice.objects.filter(status='paid')
    pending_invoices = SaleInvoice.objects.filter(status='pending')
    
    # Financial summary
    total_revenue = paid_invoices.aggregate(total=Sum('total'))['total'] or Decimal('0')
    pending_revenue = pending_invoices.aggregate(total=Sum('total'))['total'] or Decimal('0')

    total_amount = total_revenue + pending_revenue
    pending_percentage = (pending_revenue / total_amount * 100) if total_amount > 0 else 0
    
    # Customer balances
    customer_balances = Customer.objects.filter(
        balance__gt=0
    ).order_by('-balance')[:20]
    
    context = {
        'profile': profile,
        'subscription': subscription,
        'total_revenue': total_revenue,
        'pending_revenue': pending_revenue,
        'pending_percentage': pending_percentage,
        'customer_balances': customer_balances,
        'paid_invoices_count': paid_invoices.count(),
        'pending_invoices_count': pending_invoices.count(),
    }
    
    return render(request, UI_TEMPLATES["accounts"], context)


def security(request):
    """Security and permissions overview"""
    # Get security-related statistics
    total_users = User.objects.count()
    admin_users = User.objects.filter(groups__name='مدير النظام').count()
    accountant_users = User.objects.filter(groups__name='المحاسب').count()
    warehouse_users = User.objects.filter(groups__name='مدير المستودع').count()
    sales_users = User.objects.filter(groups__name='قسم المبيعات').count()
    staff_users = User.objects.filter(is_staff=True).count()
    active_users = User.objects.filter(is_active=True).count()
    
    # Recent user activities (you can implement logging later)
    recent_users = User.objects.order_by('-last_login')[:10]
    
    context = {
        'total_users': total_users,
        'admin_users': admin_users,
        'accountant_users': accountant_users,
        'warehouse_users': warehouse_users,
        'sales_users': sales_users,
        'staff_users': staff_users,
        'active_users': active_users,
        'recent_users': recent_users,
    }
    
    return render(request, UI_TEMPLATES["security"], context)


@login_required
def security_2fa(request):
    """Two-factor authentication settings page"""
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'enable':
            import secrets
            secret = secrets.token_urlsafe(32)
            profile.two_factor_secret = secret
            profile.two_factor_enabled = True
            profile.save()
            messages.success(request, 'تم تفعيل المصادقة الثنائية بنجاح')
        elif action == 'disable':
            profile.two_factor_enabled = False
            profile.two_factor_secret = ''
            profile.save()
            messages.success(request, 'تم تعطيل المصادقة الثنائية')

    total_users = User.objects.filter(is_active=True).count()
    two_fa_enabled = UserProfile.objects.filter(
        user__is_active=True,
        two_factor_enabled=True,
    ).count()
    percentage = int((two_fa_enabled / total_users * 100)) if total_users > 0 else 0

    context = {
        'total_users': total_users,
        'two_fa_enabled': two_fa_enabled,
        'percentage': percentage,
        'user_2fa_enabled': profile.two_factor_enabled,
    }

    return render(request, 'security_2fa.html', context)


@login_required
def security_password_policy(request):
    """Password policy settings page"""
    context = {
        'min_length': 8,
        'require_uppercase': True,
        'require_lowercase': True,
        'require_numbers': True,
        'require_symbols': False,
        'password_expiry_days': 90,
        'reuse_block_count': 5,
    }

    return render(request, 'security_password_policy.html', context)


@login_required
@login_required
def add_role(request):
    """Add a new role/group to the system"""
    if request.method == 'POST':
        try:
            role_name = request.POST.get('name', '').strip()
            role_description = request.POST.get('description', '').strip()
            require_2fa = request.POST.get('require_2fa') == 'on'
            permission_level = request.POST.get('permission_level', 'standard')
            
            # Validation
            if not role_name or len(role_name) < 3:
                return JsonResponse({
                    'success': False,
                    'message': 'اسم الدور يجب أن يكون 3 أحرف على الأقل'
                })
            
            # Check if role already exists
            if Group.objects.filter(name=role_name).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'هذا الدور موجود بالفعل في النظام'
                })
            
            # Create the new group
            group = Group.objects.create(name=role_name)
            
            # Assign default permissions based on permission level
            if permission_level == 'limited':
                # Only view permissions
                permissions = Permission.objects.filter(codename__startswith='view_')
            elif permission_level == 'standard':
                # View, add, change permissions (no delete)
                permissions = Permission.objects.filter(
                    Q(codename__startswith='view_') |
                    Q(codename__startswith='add_') |
                    Q(codename__startswith='change_')
                )
            elif permission_level == 'advanced':
                # All permissions except user management
                permissions = Permission.objects.exclude(
                    content_type__app_label='auth'
                )
            else:  # custom
                # No default permissions, can be set later
                permissions = []
            
            group.permissions.set(permissions)
            
            # Create default role permissions for the new group
            from .models import Module, RolePermission
            modules = Module.objects.all()
            
            # Set permissions based on level
            for module in modules:
                for action in ['view', 'add', 'change', 'delete', 'export']:
                    is_allowed = False
                    
                    if permission_level == 'limited':
                        is_allowed = action == 'view'
                    elif permission_level == 'standard':
                        is_allowed = action in ['view', 'add', 'change']
                    elif permission_level == 'advanced':
                        is_allowed = True
                    
                    RolePermission.objects.get_or_create(
                        group=group,
                        module=module,
                        action=action,
                        defaults={'is_allowed': is_allowed}
                    )
            
            # Log the action
            SecurityLog.objects.create(
                username=request.user.username,
                action_type='role_created',
                description=f'تم إنشاء دور جديد: {role_name}',
                status='success',
                ip_address=get_client_ip(request)
            )
            
            return JsonResponse({
                'success': True,
                'message': f'تم إنشاء الدور "{role_name}" بنجاح',
                'group_id': group.id,
                'group_name': group.name
            })
            
        except Exception as e:
            import traceback
            print(f"Error in add_role: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({
                'success': False,
                'message': f'حدث خطأ: {str(e)}'
            }, status=400)
    
    return JsonResponse({'success': False, 'message': 'طريقة غير صحيحة'}, status=405)



@login_required
def get_role_permissions(request, role_name):
    """Get permissions for a specific role"""
    try:
        from .models import Module, RolePermission
        
        # Get the group
        group = Group.objects.get(name=role_name)
        
        # Get all modules
        modules = Module.objects.all()
        
        # Build response
        modules_data = []
        for module in modules:
            permissions = RolePermission.objects.filter(
                group=group,
                module=module
            ).values_list('action', 'is_allowed')
            
            perm_dict = {action: is_allowed for action, is_allowed in permissions}
            
            modules_data.append({
                'id': module.id,
                'name_ar': module.name_ar,
                'name_en': module.name_en,
                'description_ar': module.description_ar,
                'description_en': module.description_en,
                'icon': module.icon,
                'color': module.color,
                'order': module.order,
                'permissions': perm_dict
            })
        
        return JsonResponse({
            'success': True,
            'role': role_name,
            'modules': modules_data
        })
    
    except Group.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'الدور غير موجود'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'حدث خطأ: {str(e)}'
        })


@login_required
def update_role_permissions(request):
    """Update role permissions"""
    if request.method == 'POST':
        try:
            from .models import Module, RolePermission
            
            data = json.loads(request.body)
            role_name = data.get('role_name')
            permissions = data.get('permissions', {})  # {module_id: {action: is_allowed}}
            
            # Get the group
            group = Group.objects.get(name=role_name)
            
            # Update permissions
            for module_id_str, actions_dict in permissions.items():
                module_id = int(module_id_str)
                module = Module.objects.get(id=module_id)
                
                for action, is_allowed in actions_dict.items():
                    RolePermission.objects.filter(
                        group=group,
                        module=module,
                        action=action
                    ).update(is_allowed=is_allowed)
            
            # Log the action
            SecurityLog.objects.create(
                username=request.user.username,
                action_type='permission_change',
                description=f'تم تحديث صلاحيات الدور: {role_name}',
                status='success',
                ip_address=get_client_ip(request)
            )
            
            return JsonResponse({
                'success': True,
                'message': 'تم تحديث الصلاحيات بنجاح'
            })
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'حدث خطأ: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'طريقة غير صحيحة'})


@login_required
def delete_role(request):
    """Delete a role/group from the system"""
    if request.method == 'POST':
        try:
            from .models import RolePermission
            
            data = json.loads(request.body)
            role_name = data.get('role_name', '').strip()
            
            # Validate
            if not role_name:
                return JsonResponse({
                    'success': False,
                    'message': 'اسم الدور مطلوب'
                })
            
            # Prevent deletion of default roles
            default_roles = ['مدير النظام', 'قسم المبيعات', 'المحاسب', 'مدير المستودع']
            if role_name in default_roles:
                return JsonResponse({
                    'success': False,
                    'message': 'لا يمكن حذف الأدوار الافتراضية من النظام'
                })
            
            # Check if role exists
            group = Group.objects.filter(name=role_name).first()
            if not group:
                return JsonResponse({
                    'success': False,
                    'message': 'الدور غير موجود'
                })
            
            # Check if role has users
            if group.user_set.count() > 0:
                return JsonResponse({
                    'success': False,
                    'message': f'لا يمكن حذف الدور لأنه موجود لديه {group.user_set.count()} مستخدمين'
                })
            
            # Delete associated permissions
            RolePermission.objects.filter(group=group).delete()
            
            # Delete the group
            group.delete()
            
            # Log the action
            SecurityLog.objects.create(
                username=request.user.username,
                action_type='role_deleted',
                description=f'تم حذف الدور: {role_name}',
                status='success',
                ip_address=get_client_ip(request)
            )
            
            return JsonResponse({
                'success': True,
                'message': f'تم حذف الدور "{role_name}" بنجاح'
            })
            
        except Exception as e:
            import traceback
            print(f"Error in delete_role: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({
                'success': False,
                'message': f'حدث خطأ: {str(e)}'
            }, status=400)
    
    return JsonResponse({'success': False, 'message': 'طريقة غير صحيحة'}, status=405)


def security_logs(request):
    """View all security logs and audit trail"""
    from .models import SecurityLog
    
    # Get filter parameters
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    action_filter = request.GET.get('action', '')
    
    # Base queryset
    logs = SecurityLog.objects.all()
    
    # Apply filters
    if search_query:
        logs = logs.filter(
            Q(username__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(ip_address__icontains=search_query)
        )
    
    if status_filter:
        logs = logs.filter(status=status_filter)
    
    if action_filter:
        logs = logs.filter(action_type=action_filter)
    
    # Get statistics
    total_logs = SecurityLog.objects.count()
    success_logs = SecurityLog.objects.filter(status='success').count()
    warning_logs = SecurityLog.objects.filter(status='warning').count()
    failed_logs = SecurityLog.objects.filter(status='failed').count()
    
    context = {
        'logs': logs[:100],  # Limit to 100 recent logs
        'total_logs': total_logs,
        'success_logs': success_logs,
        'warning_logs': warning_logs,
        'failed_logs': failed_logs,
        'search_query': search_query,
        'status_filter': status_filter,
        'action_filter': action_filter,
        'action_types': SecurityLog.ACTION_TYPES,
        'status_choices': SecurityLog.STATUS_CHOICES,
    }
    
    return render(request, 'security_logs.html', context)


def locale_time(request):
    """Localization and time zone settings"""
    # Get or create user profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Get company settings for preview
    settings_obj = CompanySettings.objects.first()
    if not settings_obj:
        settings_obj = CompanySettings.objects.create()
    
    context = {
        'system_language': profile.system_language,
        'report_language': profile.report_language,
        'timezone': profile.timezone,
        'use_24hour_format': profile.use_24hour_format,
        'date_format': profile.date_format,
        'calendar_type': profile.calendar_type,
        'company_name_ar': settings_obj.company_name_ar,
    }
    
    return render(request, UI_TEMPLATES["locale_time"], context)


def print_templates(request):
    """Print template management - load actual templates from database"""
    if request.method == 'POST':
        """Handle AJAX request to change template"""
        data = json.loads(request.body)
        template_id = data.get('template_id')
        template_type = data.get('template_type')
        document_id = data.get('document_id')  # Invoice or PO ID if provided
        
        try:
            template = PrintTemplate.objects.get(id=template_id, template_type=template_type)
            
            # If specific document provided, update that document
            if document_id:
                if template_type == 'sales_invoice':
                    invoice = SaleInvoice.objects.get(id=document_id)
                    invoice.print_template = template
                    invoice.save()
                    description = f'تم تغيير نموذج طباعة الفاتورة {invoice.number} إلى: {template.name}'
                elif template_type == 'purchase_order':
                    po = PurchaseOrder.objects.get(id=document_id)
                    po.print_template = template
                    po.save()
                    description = f'تم تغيير نموذج طباعة أمر الشراء {po.number} إلى: {template.name}'
            else:
                # Otherwise set as default for all future documents
                PrintTemplate.objects.filter(template_type=template_type).update(is_default=False)
                template.is_default = True
                template.save()
                description = f'تم تغيير نموذج الطباعة الافتراضي: {template.name}'
            
            # Log the security action (only if user is authenticated)
            if request.user.is_authenticated:
                SecurityLog.objects.create(
                    user=request.user,
                    username=request.user.username,
                    action_type='settings_change',
                    description=description,
                    ip_address=get_client_ip(request),
                    status='success'
                )
            
            return JsonResponse({'success': True, 'message': 'تم تحديث النموذج بنجاح'})
        except (PrintTemplate.DoesNotExist, SaleInvoice.DoesNotExist, PurchaseOrder.DoesNotExist):
            return JsonResponse({'success': False, 'message': 'البيان المطلوب غير موجود'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    
    # Get all templates from database
    sales_templates = PrintTemplate.objects.filter(
        template_type='sales_invoice',
        is_active=True
    ).order_by('-is_default', 'name')
    
    purchase_templates = PrintTemplate.objects.filter(
        template_type='purchase_order',
        is_active=True
    ).order_by('-is_default', 'name')
    
    inventory_templates = PrintTemplate.objects.filter(
        template_type='inventory_report',
        is_active=True
    ).order_by('-is_default', 'name')
    
    customer_templates = PrintTemplate.objects.filter(
        template_type='customer_statement',
        is_active=True
    ).order_by('-is_default', 'name')
    
    # Company settings
    company_settings = CompanySettings.objects.first()
    default_sales_template = sales_templates.filter(is_default=True).first() or sales_templates.first()
    
    context = {
        'sales_templates': sales_templates,
        'purchase_templates': purchase_templates,
        'inventory_templates': inventory_templates,
        'customer_templates': customer_templates,
        'company_settings': company_settings,
        'default_sales_template': default_sales_template,
    }
    
    return render(request, UI_TEMPLATES["print_templates"], context)


def inventory(request):
    """Inventory management with stock tracking and advanced filtering"""
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="inventory.csv"'
        response.write('\ufeff')
        response.write('product,sku,category,quantity,reorder_level,price,total_value\n')
        for item in InventoryItem.objects.select_related('product', 'product__category').order_by('-updated_at'):
            category_name = item.product.category.name if item.product.category else "بدون تصنيف"
            total_value = item.product.price * item.quantity
            response.write(
                f"{item.product.name},{item.product.sku},{category_name},{item.quantity},{item.reorder_level},{item.product.price},{total_value}\n"
            )
        return response
    
    # Base query with related objects
    inventory_items = InventoryItem.objects.select_related('product', 'product__category').order_by('-updated_at')
    
    # Search filter
    search_query = request.GET.get('search', '').strip()
    if search_query:
        inventory_items = inventory_items.filter(
            Q(product__name__icontains=search_query) |
            Q(product__sku__icontains=search_query)
        )
    
    # Category filter
    category_filter = request.GET.get('category', '').strip()
    if category_filter:
        inventory_items = inventory_items.filter(product__category__id=category_filter)
    
    # Stock status filter
    stock_status = request.GET.get('stock_status', '').strip()
    if stock_status == 'available':
        inventory_items = inventory_items.filter(quantity__gt=F('reorder_level'))
    elif stock_status == 'low':
        inventory_items = inventory_items.filter(quantity__lte=F('reorder_level'), quantity__gt=0)
    elif stock_status == 'out':
        inventory_items = inventory_items.filter(quantity=0)
    
    # Price range filter
    price_min = request.GET.get('price_min', '').strip()
    price_max = request.GET.get('price_max', '').strip()
    if price_min:
        inventory_items = inventory_items.filter(product__price__gte=Decimal(price_min))
    if price_max:
        inventory_items = inventory_items.filter(product__price__lte=Decimal(price_max))
    
    # Pagination
    page = int(request.GET.get('page', 1))
    per_page = 15
    total_count = inventory_items.count()
    total_pages = (total_count + per_page - 1) // per_page
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    inventory_items_page = inventory_items[start_idx:end_idx]
    start_display = start_idx + 1 if total_count > 0 else 0
    end_display = end_idx if end_idx < total_count else total_count
    
    # Calculate statistics on filtered items
    all_inventory = InventoryItem.objects.select_related('product', 'product__category')
    total_items = all_inventory.count()
    low_stock_count = all_inventory.filter(quantity__lte=F('reorder_level')).count()
    total_stock_value = Decimal('0')
    for item in all_inventory:
        total_stock_value += item.product.price * item.quantity
    
    # Get categories for filter dropdown
    categories = Category.objects.filter(products__isnull=False).distinct().order_by('name')
    
    context = {
        'inventory_items': inventory_items_page,
        'total_items': total_items,
        'total_count': total_count,
        'low_stock_count': low_stock_count,
        'total_stock_value': total_stock_value,
        'categories': categories,
        'current_page': page,
        'total_pages': total_pages,
        'start_display': start_display,
        'end_display': end_display,
        'search_query': search_query,
        'category_filter': category_filter,
        'stock_status': stock_status,
        'price_min': price_min,
        'price_max': price_max,
    }
    
    return render(request, UI_TEMPLATES["inventory"], context)


def warehouses(request):
    """Warehouses management page"""
    from django.db.models import Q
    
    # Get filter parameters
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', 'all')
    
    # Base queryset
    warehouses_list = Warehouse.objects.all().order_by('-created_at')
    
    # Apply search filter
    if search_query:
        warehouses_list = warehouses_list.filter(
            Q(name__icontains=search_query) |
            Q(location__icontains=search_query)
        )
    
    # Apply status filter
    if status_filter and status_filter != 'all':
        warehouses_list = warehouses_list.filter(status=status_filter)
    
    # Calculate statistics
    total_warehouses = Warehouse.objects.count()
    active_warehouses = Warehouse.objects.filter(status=Warehouse.STATUS_ACTIVE).count()
    inactive_warehouses = Warehouse.objects.filter(status=Warehouse.STATUS_INACTIVE).count()
    
    context = {
        'warehouses': warehouses_list,
        'total_warehouses': total_warehouses,
        'active_warehouses': active_warehouses,
        'inactive_warehouses': inactive_warehouses,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, UI_TEMPLATES["warehouses"], context)


def purchases(request):
    """Purchase order management"""
    from django.db.models import Sum, Count, Q
    from decimal import Decimal
    
    # Get user profile for dynamic header
    user_profile = None
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            pass
    
    # Get filter from query params
    status_filter = request.GET.get('status', 'all')
    supplier_filter = request.GET.get('supplier')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    amount_min = request.GET.get('amount_min')
    amount_max = request.GET.get('amount_max')
    search_query = request.GET.get('search', '').strip()  # ✅ إضافة البحث
    
    all_orders = PurchaseOrder.objects.select_related('supplier').order_by('-issued_date')
    
    # Apply filter based on tab
    if status_filter == 'processing':
        filtered_orders = all_orders.filter(Q(status='draft') | Q(status='pending'))
    elif status_filter == 'received':
        filtered_orders = all_orders.filter(Q(status='received') | Q(status='completed'))
    elif status_filter == 'cancelled':
        filtered_orders = all_orders.filter(status='cancelled')
    else:  # 'all'
        filtered_orders = all_orders
    
    # Apply search query
    if search_query:  # ✅ تطبيق البحث
        filtered_orders = filtered_orders.filter(
            Q(number__icontains=search_query) |
            Q(supplier__name__icontains=search_query) |
            Q(notes__icontains=search_query)
        )
    
    # Apply advanced filters
    if supplier_filter:
        filtered_orders = filtered_orders.filter(supplier_id=supplier_filter)
    if date_from:
        filtered_orders = filtered_orders.filter(issued_date__gte=date_from)
    if date_to:
        filtered_orders = filtered_orders.filter(issued_date__lte=date_to)
    if amount_min:
        filtered_orders = filtered_orders.filter(total__gte=amount_min)
    if amount_max:
        filtered_orders = filtered_orders.filter(total__lte=amount_max)

    purchase_orders = filtered_orders[:50]
    
    # Statistics
    total_orders = all_orders.count()
    processing_orders = all_orders.filter(Q(status='draft') | Q(status='pending') | Q(status='sent')).count()
    pending_orders = all_orders.filter(Q(status='pending') | Q(status='sent')).count()
    completed_orders = all_orders.filter(Q(status='received') | Q(status='completed')).count()
    cancelled_orders = all_orders.filter(status='cancelled').count()
    
    # Financial stats
    total_amount = all_orders.aggregate(total=Sum('total'))['total'] or Decimal('0.00')
    
    # Map status for template
    STATUS_MAP = {
        'draft': 'قيد المعالجة',
        'sent': 'بانتظار الاستلام',
        'received': 'تم الاستلام',
        'pending': 'بانتظار الاستلام',
        'completed': 'تم الاستلام',
        'cancelled': 'ملغي',
    }
    
    # Add mapped status to each order
    for order in purchase_orders:
        order.status_display = STATUS_MAP.get(order.status, order.status)
    
    context = {
        'purchase_orders': purchase_orders,
        'total_orders': total_orders,
        'processing_orders': processing_orders,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'cancelled_orders': cancelled_orders,
        'total_amount': total_amount,
        'current_filter': status_filter,
        'user_profile': user_profile,
        'suppliers': Supplier.objects.all(),
        'search_query': search_query,  # ✅ إضافة search_query للسياق
        'filters': {
            'supplier': supplier_filter,
            'date_from': date_from,
            'date_to': date_to,
            'amount_min': amount_min,
            'amount_max': amount_max,
        },
    }
    
    return render(request, UI_TEMPLATES["purchases"], context)


def purchase_search(request):
    """Search for purchase orders via AJAX"""
    import json
    from django.db.models import Q
    
    query = request.GET.get('q', '').strip()
    orders = PurchaseOrder.objects.select_related('supplier').order_by('-issued_date')
    
    if query:
        orders = orders.filter(
            Q(number__icontains=query) |
            Q(supplier__name__icontains=query) |
            Q(notes__icontains=query)
        )[:10]
    
    results = [{
        'id': order.id,
        'number': order.number,
        'supplier': order.supplier.name,
        'total': str(order.total),
        'status': order.status,
    } for order in orders]
    
    return JsonResponse({'results': results})


def purchase_export(request):
    """Export purchase orders to Excel CSV"""
    import csv
    from datetime import datetime
    
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="purchases_{datetime.now().strftime("%Y%m%d")}.csv"'
    response.write('\ufeff')  # BOM for Excel
    
    writer = csv.writer(response)
    writer.writerow(['رقم الطلب', 'المورد', 'تاريخ الطلب', 'المبلغ الإجمالي', 'الحالة', 'الملاحظات'])
    
    orders = PurchaseOrder.objects.select_related('supplier').order_by('-issued_date')
    status_map = {
        'draft': 'قيد المعالجة',
        'sent': 'بانتظار الاستلام',
        'received': 'تم الاستلام',
        'pending': 'بانتظار الاستلام',
        'completed': 'تم الاستلام',
        'cancelled': 'ملغي',
    }
    
    for order in orders:
        writer.writerow([
            order.number,
            order.supplier.name,
            order.issued_date.strftime('%Y-%m-%d'),
            float(order.total),
            status_map.get(order.status, order.status),
            order.notes or '',
        ])
    
    return response


def purchase_form(request):
    """Create or edit purchase order"""
    if request.method == 'POST':
        supplier_id = request.POST.get('supplier_id')
        issued_date = request.POST.get('issued_date')
        total = request.POST.get('total')
        notes = request.POST.get('notes', '')
        
        from datetime import date
        try:
            po_number = f'PO-{date.today().strftime("%Y%m%d")}-{PurchaseOrder.objects.count() + 1:04d}'
            order = PurchaseOrder.objects.create(
                number=po_number,
                supplier_id=supplier_id,
                issued_date=issued_date,
                total=total,
                notes=notes,
                status='draft'
            )
            return JsonResponse({'success': True, 'order_id': order.id, 'message': 'تم إنشاء الطلب بنجاح!'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    suppliers = Supplier.objects.all()
    context = {'suppliers': suppliers}
    return render(request, 'purchase_form.html', context)


def supplier_quick_create(request):
    """Create supplier quickly from purchases modal"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

    name = request.POST.get('name', '').strip()
    email = request.POST.get('email', '').strip()
    phone = request.POST.get('phone', '').strip()

    if not name:
        return JsonResponse({'success': False, 'error': 'اسم المورد مطلوب'}, status=400)

    supplier = Supplier.objects.create(
        name=name,
        email=email,
        phone=phone,
        is_active=True,
    )

    return JsonResponse({
        'success': True,
        'supplier': {
            'id': supplier.id,
            'name': supplier.name,
        }
    })


@login_required(login_url='login')
def taxes(request):
    """Tax rate management"""
    tax_rates = TaxRate.objects.filter(is_default=True).order_by('name') | TaxRate.objects.filter(is_default=False).order_by('name')
    default_tax = TaxRate.objects.filter(is_default=True).first()
    company_settings = CompanySettings.objects.first()
    if company_settings is None:
        company_settings = CompanySettings.objects.create()
    
    context = {
        'tax_rates': tax_rates,
        'default_tax': default_tax,
        'tax_count': tax_rates.count(),
        'company_settings': company_settings,
        'vat_id': company_settings.vat_number,
    }
    
    return render(request, UI_TEMPLATES["taxes"], context)


def taxes_save(request):
    """Save tax settings"""
    if request.method == 'POST':
        try:
            company_settings = CompanySettings.objects.first()
            if company_settings is None:
                company_settings = CompanySettings.objects.create()
            
            # Handle individual field updates or full form
            if 'vat_number' in request.POST:
                vat_number = request.POST.get('vat_number', '').strip()
                company_settings.vat_number = vat_number
            
            if 'default_tax_rate' in request.POST:
                default_tax_rate = request.POST.get('default_tax_rate', '0')
                try:
                    tax_rate = float(default_tax_rate)
                    if tax_rate < 0 or tax_rate > 100:
                        return JsonResponse({'success': False, 'message': 'معدل الضريبة يجب أن يكون بين 0 و 100'})
                    company_settings.default_tax_rate = tax_rate
                except (ValueError, TypeError):
                    return JsonResponse({'success': False, 'message': 'معدل الضريبة غير صحيح'})
            
            if 'prices_include_tax' in request.POST:
                prices_include_tax = request.POST.get('prices_include_tax', 'true') == 'true'
                company_settings.prices_include_tax = prices_include_tax
            
            # Save to database
            company_settings.save()
            
            return JsonResponse({
                'success': True, 
                'message': 'تم حفظ الإعدادات بنجاح'
            })
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'message': f'حدث خطأ: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'طلب غير صحيح'})


def notifications(request):
    """Notification center with filtering and statistics"""
    # Get all notifications ordered by most recent
    all_notifications = Notification.objects.order_by('-created_at')
    
    # Notifications by category
    recent_notifications = all_notifications.filter(is_read=False)[:20]
    read_notifications = all_notifications.filter(is_read=True)[:50]
    
    # Statistics
    unread_count = all_notifications.filter(is_read=False).count()
    total_count = all_notifications.count()
    
    # Notifications by type/level
    error_count = all_notifications.filter(level='error').count()
    warning_count = all_notifications.filter(level='warning').count()
    success_count = all_notifications.filter(level='success').count()
    
    # Get user profile info
    user_profile = None
    if request.user.is_authenticated:
        try:
            user_profile = request.user.profile
        except:
            pass
    
    context = {
        'notifications': all_notifications[:50],  # Show all for tab switching
        'recent_notifications': recent_notifications,
        'read_notifications': read_notifications,
        'unread_count': unread_count,
        'total_count': total_count,
        'error_count': error_count,
        'warning_count': warning_count,
        'success_count': success_count,
        'user_profile': user_profile,
    }
    
    return render(request, UI_TEMPLATES["notifications"], context)


def users_permissions(request):
    """User and permission management"""
    # Get filter parameter
    filter_role = request.GET.get('role', None)
    
    # Get or create groups
    admin_group, _ = Group.objects.get_or_create(name='مدير النظام')
    accountant_group, _ = Group.objects.get_or_create(name='المحاسب')
    warehouse_group, _ = Group.objects.get_or_create(name='مدير المستودع')
    sales_group, _ = Group.objects.get_or_create(name='قسم المبيعات')
    
    # Filter users based on role
    users = User.objects.all().prefetch_related('groups')
    
    if filter_role == 'admin':
        users = users.filter(groups__name='مدير النظام')
    elif filter_role == 'accountant':
        users = users.filter(groups__name='المحاسب')
    elif filter_role == 'sales':
        users = users.filter(groups__name='قسم المبيعات')
    
    users = users.order_by('-date_joined')
    
    # Statistics (always show total counts)
    all_users = User.objects.all()
    total_users = all_users.count()
    active_users = all_users.filter(is_active=True).count()
    staff_users = all_users.filter(is_staff=True).count()
    admin_users = all_users.filter(groups__name='مدير النظام').count()
    accountant_users = all_users.filter(groups__name='المحاسب').count()
    warehouse_users = all_users.filter(groups__name='مدير المستودع').count()
    sales_users = all_users.filter(groups__name='قسم المبيعات').count()
    
    # Get all groups with their users
    groups = Group.objects.all().prefetch_related('user_set')

    # Permissions catalog (limited to key modules)
    permissions_catalog = [
        {
            'section': 'إدارة المخازن',
            'items': [
                {'app_label': 'core', 'codename': 'view_product', 'label': 'عرض المنتجات والمخزون'},
                {'app_label': 'core', 'codename': 'add_product', 'label': 'إضافة منتجات جديدة'},
                {'app_label': 'core', 'codename': 'change_inventoryitem', 'label': 'تعديل كميات المخزون'},
            ],
        },
        {
            'section': 'المبيعات والفواتير',
            'items': [
                {'app_label': 'core', 'codename': 'add_saleinvoice', 'label': 'إنشاء فواتير المبيعات'},
                {'app_label': 'core', 'codename': 'change_saleinvoice', 'label': 'إدارة المرتجعات'},
                {'app_label': 'core', 'codename': 'view_saleinvoice', 'label': 'تقارير المبيعات اليومية'},
            ],
        },
    ]

    for user in users:
        user.perm_codes = set(
            f"{app_label}.{codename}"
            for app_label, codename in user.user_permissions.values_list('content_type__app_label', 'codename')
        )
    
    context = {
        'users': users,
        'groups': groups,
        'total_users': total_users,
        'active_users': active_users,
        'staff_users': staff_users,
        'admin_users': admin_users,
        'accountant_users': accountant_users,
        'warehouse_users': warehouse_users,
        'sales_users': sales_users,
        'permissions_catalog': permissions_catalog,
        'filter_role': filter_role,
    }
    
    return render(request, UI_TEMPLATES["users_permissions"], context)


def employees(request):
    """Employees management (basic user list)"""
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')

    users = User.objects.all().prefetch_related('groups').order_by('-date_joined')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query)
            | Q(first_name__icontains=search_query)
            | Q(last_name__icontains=search_query)
            | Q(email__icontains=search_query)
        )

    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)

    context = {
        'users': users,
        'search_query': search_query,
        'status_filter': status_filter,
    }

    return render(request, 'employees.html', context)


def pages_index(request):
    pages = [
        {"name": "لوحة التحكم", "path": "dashboard", "url": "/"},
        {"name": "إدارة المبيعات", "path": "sales", "url": "/sales/"},
        {"name": "إدارة العملاء", "path": "customers", "url": "/customers/"},
        {"name": "التقارير والتحليلات", "path": "reports", "url": "/reports/"},
        {"name": "الإعدادات العامة", "path": "general_settings", "url": "/settings/general/"},
        {"name": "إدارة الحسابات", "path": "accounts", "url": "/accounts/"},
        {"name": "إدارة المخزون", "path": "inventory", "url": "/inventory/"},
        {"name": "إدارة المشتريات", "path": "purchases", "url": "/purchases/"},
        {"name": "إدارة الضرائب", "path": "taxes", "url": "/taxes/"},
        {"name": "قوالب الطباعة", "path": "print_templates", "url": "/print-templates/"},
        {"name": "مركز التنبيهات", "path": "notifications", "url": "/notifications/"},
        {"name": "الأمان والصلاحيات", "path": "security", "url": "/security/"},
        {"name": "اللغة والوقت", "path": "locale_time", "url": "/locale-time/"},
        {"name": "المستخدمون والصلاحيات", "path": "users_permissions", "url": "/users-permissions/"},
        {"name": "إعدادات النظام", "path": "system_settings", "url": "/settings/system/"},
    ]
    return render(request, "index.html", {"pages": pages})


def api_summary(request):
    invoices_total = (
        SaleInvoice.objects.aggregate(total=Sum("total"))
        if SaleInvoice.objects.exists()
        else {"total": Decimal("0")}
    )
    customers_count = Customer.objects.count()
    products_count = Product.objects.count()
    low_stock = InventoryItem.objects.filter(quantity__lte=F("reorder_level")).count()

    payload = {
        "generated_at": date.today().isoformat(),
        "invoices_total": float(invoices_total["total"] or 0),
        "customers_count": customers_count,
        "products_count": products_count,
        "low_stock": low_stock,
    }
    return JsonResponse(payload)


def api_alerts(request):
    alerts = Notification.objects.order_by("-created_at")[:5]
    data = [
        {
            "title": alert.title,
            "message": alert.message,
            "level": alert.level,
            "created_at": alert.created_at.isoformat(),
        }
        for alert in alerts
    ]
    return JsonResponse({"alerts": data})


# ============================================================================
# CRUD Operations for Customers
# ============================================================================

def customer_create(request):
    """Create a new customer"""
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            messages.success(request, f'تم إضافة العميل {customer.name} بنجاح')
            return redirect('customers')
    else:
        form = CustomerForm()
    
    return render(request, 'customer_form.html', {'form': form, 'action': 'إضافة'})


def customer_edit(request, pk):
    """Edit existing customer"""
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث بيانات العميل بنجاح')
            return redirect('customers')
    else:
        form = CustomerForm(instance=customer)
    
    return render(request, 'customer_form.html', {'form': form, 'action': 'تعديل', 'customer': customer})


def customer_delete(request, pk):
    """Delete customer"""
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer.delete()
        messages.success(request, 'تم حذف العميل بنجاح')
        return redirect('customers')
    
    return render(request, 'customer_confirm_delete.html', {'customer': customer})


# ============================================================================
# CRUD Operations for Products & Inventory
# ============================================================================

def product_create(request):
    """Create new product"""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            # Create inventory item for the product with initial quantity
            quantity = form.cleaned_data.get('quantity', 0)
            InventoryItem.objects.create(product=product, quantity=quantity)
            messages.success(request, f'تم إضافة المنتج {product.name} بنجاح')
            return redirect('inventory')
    else:
        form = ProductForm()
    
    return render(request, 'product_form.html', {'form': form, 'action': 'إضافة'})


def product_edit(request, pk):
    """Edit existing product"""
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            # Update inventory quantity if provided
            quantity = form.cleaned_data.get('quantity')
            if quantity is not None:
                inventory = InventoryItem.objects.filter(product=product).first()
                if inventory:
                    inventory.quantity = quantity
                    inventory.save()
                else:
                    InventoryItem.objects.create(product=product, quantity=quantity)
            messages.success(request, 'تم تحديث بيانات المنتج بنجاح')
            return redirect('inventory')
    else:
        # Load current quantity from inventory
        initial_data = {}
        inventory = InventoryItem.objects.filter(product=product).first()
        if inventory:
            initial_data['quantity'] = inventory.quantity
        form = ProductForm(instance=product, initial=initial_data)
    
    return render(request, 'product_form.html', {'form': form, 'action': 'تعديل', 'product': product})


def inventory_update(request, pk):
    """Update inventory quantity"""
    inventory_item = get_object_or_404(InventoryItem, pk=pk)
    if request.method == 'POST':
        form = InventoryItemForm(request.POST, instance=inventory_item)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث المخزون بنجاح')
            return redirect('inventory')
    else:
        form = InventoryItemForm(instance=inventory_item)
    
    return render(request, 'inventory_form.html', {'form': form, 'inventory_item': inventory_item})


# ============================================================================
# CRUD Operations for Sales Invoices
# ============================================================================

def invoice_create(request):
    """Create new sales invoice with POS interface"""
    customers = Customer.objects.filter(is_active=True)
    return render(request, 'invoice_pos.html', {'customers': customers})


def invoice_edit(request, pk):
    """Edit existing invoice"""
    invoice = get_object_or_404(SaleInvoice, pk=pk)
    if request.method == 'POST':
        form = SaleInvoiceForm(request.POST, instance=invoice)
        if form.is_valid():
            saved_invoice = form.save()
            
            # Apply default template if not already set
            if not saved_invoice.print_template:
                default_template = PrintTemplate.objects.filter(
                    template_type='sales_invoice',
                    is_default=True
                ).first()
                if default_template:
                    saved_invoice.print_template = default_template
                    saved_invoice.save()
            
            # Log the action
            SecurityLog.objects.create(
                user=request.user,
                username=request.user.username,
                action_type='settings_change',
                description=f'تم تحديث الفاتورة رقم {saved_invoice.number}',
                ip_address=get_client_ip(request),
                status='success'
            )
            
            messages.success(request, 'تم تحديث الفاتورة بنجاح')
            return redirect('sales')
    else:
        form = SaleInvoiceForm(instance=invoice)
    
    return render(request, 'invoice_form.html', {'form': form, 'action': 'تعديل', 'invoice': invoice})


def invoice_detail(request, pk):
    """View invoice details"""
    invoice = get_object_or_404(SaleInvoice, pk=pk)
    items = invoice.items.select_related('product')
    
    # Get company settings for VAT info
    company_settings = CompanySettings.objects.first()
    
    # Use invoice model methods for calculations
    subtotal = invoice.get_subtotal()
    vat_amount = invoice.get_vat_amount()
    total = invoice.get_total()
    
    context = {
        'invoice': invoice,
        'items': items,
        'subtotal': subtotal,
        'vat_amount': vat_amount,
        'total': total,
        'company_settings': company_settings,
    }
    
    return render(request, 'invoice_detail.html', context)


# ============================================================================
# CRUD Operations for Purchase Orders
# ============================================================================

def purchase_order_create(request):
    """Create new purchase order"""
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST)
        if form.is_valid():
            purchase_order = form.save()
            messages.success(request, f'تم إنشاء أمر الشراء رقم {purchase_order.number} بنجاح')
            return redirect('purchases')
    else:
        form = PurchaseOrderForm()
    
    return render(request, 'purchase_order_form.html', {'form': form, 'action': 'إنشاء'})


def purchase_order_edit(request, pk):
    """Edit existing purchase order"""
    purchase_order = get_object_or_404(PurchaseOrder, pk=pk)
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST, instance=purchase_order)
        if form.is_valid():
            saved_po = form.save()
            
            # Apply default template if not already set
            if not saved_po.print_template:
                default_template = PrintTemplate.objects.filter(
                    template_type='purchase_order',
                    is_default=True
                ).first()
                if default_template:
                    saved_po.print_template = default_template
                    saved_po.save()
            
            messages.success(request, 'تم تحديث أمر الشراء بنجاح')
            return redirect('purchases')
    else:
        form = PurchaseOrderForm(instance=purchase_order)
    
    return render(request, 'purchase_order_form.html', {'form': form, 'action': 'تعديل', 'purchase_order': purchase_order})


def purchase_order_detail(request, pk):
    """View purchase order details (read-only)"""
    purchase_order = get_object_or_404(PurchaseOrder, pk=pk)
    form = PurchaseOrderForm(instance=purchase_order)
    for field in form.fields.values():
        field.disabled = True
    return render(request, 'purchase_order_form.html', {
        'form': form,
        'action': 'عرض',
        'purchase_order': purchase_order,
        'readonly': True,
    })


# ============================================================================
# API Endpoints for AJAX Operations
# ============================================================================

def api_customer_list(request):
    """API: Get all customers"""
    customers = Customer.objects.values('id', 'name', 'email', 'phone', 'customer_type', 'balance')
    return JsonResponse(list(customers), safe=False)


def api_product_list(request):
    """API: Get all products"""
    products = Product.objects.values('id', 'name', 'sku', 'category', 'price')
    return JsonResponse(list(products), safe=False)


def api_inventory_status(request):
    """API: Get inventory status"""
    low_stock = InventoryItem.objects.filter(
        quantity__lte=F('reorder_level')
    ).select_related('product').values(
        'id', 'product__name', 'product__sku', 'quantity', 'reorder_level'
    )
    
    return JsonResponse({
        'low_stock_items': list(low_stock),
        'count': low_stock.count()
    })


def api_sales_stats(request):
    """API: Get sales statistics"""
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    stats = {
        'today': SaleInvoice.objects.filter(
            issued_date=today, status='paid'
        ).aggregate(total=Sum('total'))['total'] or 0,
        
        'this_week': SaleInvoice.objects.filter(
            issued_date__gte=week_ago, status='paid'
        ).aggregate(total=Sum('total'))['total'] or 0,
        
        'this_month': SaleInvoice.objects.filter(
            issued_date__gte=month_ago, status='paid'
        ).aggregate(total=Sum('total'))['total'] or 0,
        
        'total_invoices': SaleInvoice.objects.count(),
        'pending_invoices': SaleInvoice.objects.filter(status='pending').count(),
    }
    
    return JsonResponse(stats)


def api_dashboard_data(request):
    """API: Get comprehensive dashboard data"""
    today = timezone.now().date()
    month_ago = today - timedelta(days=30)
    
    data = {
        'sales': {
            'total': float(SaleInvoice.objects.filter(status='paid').aggregate(
                total=Sum('total'))['total'] or 0),
            'this_month': float(SaleInvoice.objects.filter(
                issued_date__gte=month_ago, status='paid'
            ).aggregate(total=Sum('total'))['total'] or 0),
            'count': SaleInvoice.objects.count(),
        },
        'customers': {
            'total': Customer.objects.count(),
            'active': Customer.objects.filter(is_active=True).count(),
            'new_this_month': Customer.objects.filter(created_at__gte=month_ago).count(),
        },
        'inventory': {
            'total_products': Product.objects.count(),
            'low_stock': InventoryItem.objects.filter(quantity__lte=F('reorder_level')).count(),
        },
        'purchases': {
            'pending': PurchaseOrder.objects.filter(status='pending').count(),
            'completed': PurchaseOrder.objects.filter(status='completed').count(),
        }
    }
    
    return JsonResponse(data)


# ========== SUPPLIER CRUD ==========

def supplier_list(request):
    """List all suppliers"""
    suppliers = Supplier.objects.all()

    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '').strip()
    order_by = request.GET.get('order', '').strip()

    if search_query:
        suppliers = suppliers.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )

    if status_filter == 'active':
        suppliers = suppliers.filter(is_active=True)
    elif status_filter == 'inactive':
        suppliers = suppliers.filter(is_active=False)

    if order_by == 'name':
        suppliers = suppliers.order_by('name')
    elif order_by == 'oldest':
        suppliers = suppliers.order_by('created_at')
    else:
        suppliers = suppliers.order_by('-created_at')
    
    total_suppliers = suppliers.count()
    active_suppliers = suppliers.filter(is_active=True).count()
    inactive_suppliers = total_suppliers - active_suppliers

    context = {
        'suppliers': suppliers,
        'total_suppliers': total_suppliers,
        'active_suppliers': active_suppliers,
        'inactive_suppliers': inactive_suppliers,
        'search_query': search_query,
        'status_filter': status_filter,
        'order_by': order_by,
    }
    
    return render(request, 'supplier_list.html', context)


def supplier_create(request):
    """Create new supplier"""
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save()
            messages.success(request, f'تم إضافة المورد: {supplier.name} بنجاح!')
            return redirect('supplier_list')
    else:
        form = SupplierForm()
    
    return render(request, 'supplier_form.html', {'form': form, 'action': 'إضافة'})


def supplier_edit(request, pk):
    """Edit existing supplier"""
    supplier = get_object_or_404(Supplier, pk=pk)
    
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, f'تم تحديث المورد: {supplier.name} بنجاح!')
            return redirect('supplier_list')
    else:
        form = SupplierForm(instance=supplier)
    
    return render(request, 'supplier_form.html', {'form': form, 'action': 'تعديل', 'supplier': supplier})


def supplier_delete(request, pk):
    """Delete supplier"""
    supplier = get_object_or_404(Supplier, pk=pk)
    
    if request.method == 'POST':
        name = supplier.name
        try:
            supplier.delete()
            messages.success(request, f'تم حذف المورد: {name}')
            return redirect('supplier_list')
        except ProtectedError:
            messages.error(request, f'لا يمكن حذف المورد "{name}" لأنه مرتبط بطلبيات شراء. يرجى حذف الطلبيات أولاً.')
            return redirect('supplier_list')
        except Exception as e:
            messages.error(request, f'حدث خطأ عند حذف المورد: {str(e)}')
            return redirect('supplier_list')
    
    return render(request, 'supplier_confirm_delete.html', {'supplier': supplier})


# ========== TAX CRUD ==========

def tax_list(request):
    """List all tax rates"""
    taxes = TaxRate.objects.all().order_by('-is_default', 'name')
    
    context = {
        'taxes': taxes,
        'total_taxes': taxes.count(),
    }
    
    return render(request, 'tax_list.html', context)


def tax_create(request):
    """Create new tax rate"""
    if request.method == 'POST':
        form = TaxRateForm(request.POST)
        if form.is_valid():
            tax = form.save()
            messages.success(request, f'تم إضافة الضريبة: {tax.name} بنجاح!')
            return redirect('taxes')
    else:
        form = TaxRateForm()
    
    return render(request, 'tax_form.html', {'form': form, 'action': 'إضافة'})


def tax_edit(request, pk):
    """Edit existing tax rate"""
    tax = get_object_or_404(TaxRate, pk=pk)
    
    if request.method == 'POST':
        form = TaxRateForm(request.POST, instance=tax)
        if form.is_valid():
            form.save()
            messages.success(request, f'تم تحديث الضريبة: {tax.name} بنجاح!')
            return redirect('taxes')
    else:
        form = TaxRateForm(instance=tax)
    
    return render(request, 'tax_form.html', {'form': form, 'action': 'تعديل', 'tax': tax})


def tax_delete(request, pk):
    """Delete tax rate"""
    tax = get_object_or_404(TaxRate, pk=pk)
    
    if request.method == 'POST':
        name = tax.name
        tax.delete()
        messages.success(request, f'تم حذف الضريبة: {name}')
        return redirect('taxes')
    
    return render(request, 'tax_confirm_delete.html', {'tax': tax})


# ========== USER MANAGEMENT ==========

def user_create(request):
    """Create new user"""
    groups = Group.objects.all().order_by('name')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Set active status
            user.is_active = request.POST.get('is_active') == 'on'
            user.save()
            
            # Assign group if selected
            group_id = request.POST.get('group_id')
            if group_id:
                try:
                    group = Group.objects.get(id=group_id)
                    user.groups.add(group)
                except Group.DoesNotExist:
                    pass
            
            messages.success(request, f'تم إنشاء المستخدم: {user.username} بنجاح!')
            return redirect('users_permissions')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'user_form.html', {
        'form': form, 
        'action': 'إضافة',
        'groups': groups
    })


def user_edit(request, pk):
    """Edit existing user"""
    user = get_object_or_404(User, pk=pk)
    groups = Group.objects.all().order_by('name')
    
    if request.method == 'POST':
        # Simple form for editing user details (not password)
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.is_active = request.POST.get('is_active') == 'on'
        user.save()

        group_id = request.POST.get('group_id')
        if group_id:
            try:
                group = Group.objects.get(id=group_id)
                user.groups.set([group])
            except Group.DoesNotExist:
                user.groups.clear()
        else:
            user.groups.clear()
        
        messages.success(request, f'تم تحديث المستخدم: {user.username} بنجاح!')
        return redirect('users_permissions')
    
    return render(request, 'user_edit_form.html', {'user': user, 'groups': groups})


def user_permissions_update(request, pk):
    """Update user permissions (selected modules)"""
    user = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        allowed = {
            ('core', 'view_product'),
            ('core', 'add_product'),
            ('core', 'change_inventoryitem'),
            ('core', 'add_saleinvoice'),
            ('core', 'change_saleinvoice'),
            ('core', 'view_saleinvoice'),
        }

        selected = request.POST.getlist('permissions')
        selected_pairs = set()
        for item in selected:
            if '.' not in item:
                continue
            app_label, codename = item.split('.', 1)
            if (app_label, codename) in allowed:
                selected_pairs.add((app_label, codename))

        from django.contrib.auth.models import Permission
        perms = Permission.objects.filter(
            content_type__app_label__in=[p[0] for p in selected_pairs],
            codename__in=[p[1] for p in selected_pairs],
        )

        user.user_permissions.set(perms)
        messages.success(request, f'تم تحديث صلاحيات المستخدم: {user.username} بنجاح')
        return redirect('users_permissions')

    return redirect('users_permissions')


def user_delete(request, pk):
    """Delete user"""
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'تم حذف المستخدم: {username}')
        return redirect('users_permissions')
    
    return render(request, 'user_confirm_delete.html', {'user': user})


# ========== SEARCH FUNCTIONALITY ==========

def search(request):
    """Global search across all entities"""
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return redirect('profile')

    query = request.GET.get('q', '')
    
    if len(query) < 2:
        return JsonResponse({'customers': [], 'products': [], 'invoices': [], 'suppliers': [], 'users': []})
    
    # Search users
    users = User.objects.filter(
        Q(username__icontains=query) | 
        Q(first_name__icontains=query) | 
        Q(last_name__icontains=query) | 
        Q(email__icontains=query)
    )[:10]
    
    users_data = []
    for user in users:
        full_name = user.get_full_name() or user.username
        initials = ''
        if user.first_name and user.last_name:
            initials = user.first_name[0] + user.last_name[0]
        elif user.first_name:
            initials = user.first_name[0]
        else:
            initials = user.username[0].upper()
        
        users_data.append({
            'id': user.id,
            'name': full_name,
            'email': user.email or '',
            'initials': initials.upper(),
            'url': f'/users/{user.id}/edit/'
        })
    
    # Search customers
    customers_data = []
    for customer in Customer.objects.filter(
        Q(name__icontains=query) | Q(email__icontains=query) | Q(phone__icontains=query)
    )[:10]:
        customers_data.append({
            'id': customer.id,
            'name': customer.name,
            'email': customer.email or '',
            'phone': customer.phone or '',
            'url': f'/customers/'
        })
    
    # Search products
    products_data = []
    for product in Product.objects.filter(
        Q(name__icontains=query) | Q(sku__icontains=query) | Q(category__name__icontains=query)
    ).select_related('category')[:10]:
        products_data.append({
            'id': product.id,
            'name': product.name,
            'sku': product.sku or '',
            'price': str(product.price),
            'category': product.category.name if product.category else '',
            'url': f'/products/{product.id}/edit/'
        })
    
    # Search invoices
    invoices_data = []
    for invoice in SaleInvoice.objects.filter(
        Q(number__icontains=query) | Q(customer__name__icontains=query)
    ).select_related('customer')[:10]:
        invoices_data.append({
            'id': invoice.id,
            'number': invoice.number,
            'customer': invoice.customer.name if invoice.customer else '',
            'total': str(invoice.total),
            'status': invoice.status,
            'url': f'/invoices/{invoice.id}/'
        })
    
    # Search suppliers
    suppliers_data = []
    for supplier in Supplier.objects.filter(
        Q(name__icontains=query) | Q(email__icontains=query)
    )[:10]:
        suppliers_data.append({
            'id': supplier.id,
            'name': supplier.name,
            'email': supplier.email or '',
            'phone': supplier.phone or '',
            'url': f'/suppliers/'
        })
    
    results = {
        'users': users_data,
        'customers': customers_data,
        'products': products_data,
        'invoices': invoices_data,
        'suppliers': suppliers_data,
    }
    
    return JsonResponse(results)


# ========== NOTIFICATION ACTIONS ==========

def notification_create(request):
    """Create new notification"""
    if request.method == 'POST':
        form = NotificationForm(request.POST)
        if form.is_valid():
            notification = form.save()
            messages.success(request, 'تم إنشاء الإشعار بنجاح!')
            return redirect('notifications')
    else:
        form = NotificationForm()
    
    return render(request, 'notification_form.html', {'form': form})


def notification_mark_all_read(request):
    """Mark all notifications as read"""
    if request.method == 'POST':
        count = Notification.objects.filter(is_read=False).update(is_read=True)
        messages.success(request, f'تم وضع علامة مقروء على {count} إشعار')
        return redirect('notifications')
    
    return redirect('notifications')


def notification_delete(request, pk):
    """Delete notification"""
    notification = get_object_or_404(Notification, pk=pk)
    
    if request.method == 'POST':
        notification.delete()
        messages.success(request, 'تم حذف الإشعار')
        return redirect('notifications')
    
    return render(request, 'notification_confirm_delete.html', {'notification': notification})


# ========== SUBSCRIPTION MANAGEMENT ==========

def subscription(request):
    """Subscription plan management page with real data"""
    from .models import Subscription
    from datetime import timedelta
    
    user = request.user
    
    # Get or create subscription
    try:
        subscription = Subscription.objects.get(user=user)
    except Subscription.DoesNotExist:
        subscription = Subscription.objects.create(
            user=user,
            plan='free',
            renewal_date=timezone.now().date() + timedelta(days=365),
            monthly_cost=0,
            storage_total=5
        )
    
    # Available plans with upgrade links
    available_plans = [
        {
            'id': 'basic',
            'name': 'الأساسية',
            'name_en': 'Basic',
            'price': 49.00,
            'users': 5,
            'storage': 5,
            'features': ['تقارير أساسية', 'دعم بريد إلكتروني', 'نسخ احتياطي أسبوعي']
        },
        {
            'id': 'professional',
            'name': 'الاحترافية',
            'name_en': 'Professional',
            'price': 149.00,
            'users': 50,
            'storage': 100,
            'features': ['تقارير متقدمة', 'دعم فني 24/7', 'نسخ احتياطي يومي', 'تكامل API']
        },
        {
            'id': 'enterprise',
            'name': 'المؤسسية',
            'name_en': 'Enterprise',
            'price': 499.00,
            'users': 'غير محدود',
            'storage': 'غير محدود',
            'features': ['كل المميزات', 'دعم مخصص 24/7', 'تدريب فريقك', 'تخصيص كامل', 'مدير حساب مخصص']
        }
    ]
    
    context = {
        'subscription': subscription,
        'available_plans': available_plans,
        'user': user,
    }
    
    return render(request, 'subscription.html', context)


# ============================================
# CATEGORY MANAGEMENT VIEWS
# ============================================

def categories_list(request):
    """List all categories"""
    categories = Category.objects.filter(parent__isnull=True).prefetch_related('subcategories')
    return render(request, 'categories_list.html', {'categories': categories})


def category_create(request):
    """Create new category"""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'تم إضافة الفئة "{category.name}" بنجاح')
            return redirect('categories_list')
    else:
        form = CategoryForm()
    return render(request, 'category_form.html', {'form': form, 'title': 'إضافة فئة جديدة'})


def category_edit(request, pk):
    """Edit existing category"""
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f'تم تحديث الفئة "{category.name}" بنجاح')
            return redirect('categories_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'category_form.html', {'form': form, 'title': 'تعديل الفئة', 'category': category})


def category_delete(request, pk):
    """Delete category (with validation)"""
    category = get_object_or_404(Category, pk=pk)
    
    # Check if category has products
    if category.products.exists():
        messages.error(request, f'لا يمكن حذف الفئة "{category.name}" لأنها تحتوي على منتجات')
        return redirect('categories_list')
    
    # Check if category has subcategories
    if category.subcategories.exists():
        messages.error(request, f'لا يمكن حذف الفئة "{category.name}" لأنها تحتوي على فئات فرعية')
        return redirect('categories_list')
    
    category_name = category.name
    category.delete()
    messages.success(request, f'تم حذف الفئة "{category_name}" بنجاح')
    return redirect('categories_list')


# ============================================
# WAREHOUSE CRUD OPERATIONS
# ============================================

def warehouse_create(request):
    """Create new warehouse"""
    if request.method == 'POST':
        form = WarehouseForm(request.POST)
        if form.is_valid():
            warehouse = form.save()
            messages.success(request, f'تم إضافة المستودع "{warehouse.name}" بنجاح')
            return redirect('warehouses')
    else:
        form = WarehouseForm()
    
    return render(request, 'warehouse_form.html', {'form': form, 'title': 'إضافة مستودع جديد'})


def warehouse_edit(request, pk):
    """Edit existing warehouse"""
    warehouse = get_object_or_404(Warehouse, pk=pk)
    
    if request.method == 'POST':
        form = WarehouseForm(request.POST, instance=warehouse)
        if form.is_valid():
            warehouse = form.save()
            messages.success(request, f'تم تحديث المستودع "{warehouse.name}" بنجاح')
            return redirect('warehouses')
    else:
        form = WarehouseForm(instance=warehouse)
    
    return render(request, 'warehouse_form.html', {
        'form': form, 
        'warehouse': warehouse,
        'title': f'تعديل المستودع: {warehouse.name}'
    })


def warehouse_view(request, pk):
    """View warehouse details"""
    warehouse = get_object_or_404(Warehouse, pk=pk)
    return render(request, 'warehouse_detail.html', {'warehouse': warehouse})


def warehouse_delete(request, pk):
    """Delete warehouse"""
    warehouse = get_object_or_404(Warehouse, pk=pk)
    warehouse_name = warehouse.name
    warehouse.delete()
    messages.success(request, f'تم حذف المستودع "{warehouse_name}" بنجاح')
    return redirect('warehouses')


# ============================================
# API ENDPOINTS FOR POS
# ============================================

def api_search_products(request):
    """Search products by name for POS"""
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'products': []})
    
    products = Product.objects.filter(
        name__icontains=query,
        is_active=True
    ).select_related('category', 'inventory')[:10]
    
    results = []
    for product in products:
        try:
            stock = product.inventory.quantity
        except:
            stock = 0
            
        results.append({
            'id': product.id,
            'name': product.name,
            'sku': product.sku,
            'price': float(product.get_display_price()),
            'regular_price': float(product.price),
            'sale_price': float(product.sale_price) if product.sale_price else None,
            'stock': stock,
            'image': product.image.url if product.image else None,
            'category': product.category.name if product.category else ''
        })
    
    return JsonResponse({'products': results})


def api_submit_invoice(request):
    """Submit invoice with stock validation"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'يجب استخدام POST'}, status=405)
    
    import json
    data = json.loads(request.body)
    
    customer_id = data.get('customer_id')
    items = data.get('items', [])
    
    if not customer_id:
        return JsonResponse({'success': False, 'error': 'يرجى اختيار عميل'})
    
    if not items:
        return JsonResponse({'success': False, 'error': 'يرجى إضافة منتجات'})
    
    # Validate stock for all items
    for item in items:
        product = Product.objects.get(id=item['product_id'])
        try:
            inventory = product.inventory
            if inventory.quantity < item['quantity']:
                return JsonResponse({
                    'success': False,
                    'error': f'المخزون غير كافٍ للمنتج "{product.name}". المتوفر: {inventory.quantity}'
                })
        except:
            return JsonResponse({
                'success': False,
                'error': f'لا يوجد مخزون للمنتج "{product.name}"'
            })
    
    # Create invoice
    from datetime import date
    customer = Customer.objects.get(id=customer_id)
    invoice_number = f'INV-{date.today().strftime("%Y%m%d")}-{SaleInvoice.objects.count() + 1:04d}'
    
    # Get default print template
    default_template = PrintTemplate.objects.filter(
        template_type='sales_invoice',
        is_default=True
    ).first()
    
    invoice = SaleInvoice.objects.create(
        number=invoice_number,
        customer=customer,
        issued_date=date.today(),
        status=SaleInvoice.STATUS_PAID,
        print_template=default_template,
        total=0
    )
    
    total = Decimal('0.00')
    
    # Create items and reduce stock
    for item in items:
        product = Product.objects.get(id=item['product_id'])
        quantity = item['quantity']
        unit_price = Decimal(str(item['price']))
        subtotal = unit_price * quantity
        
        SaleItem.objects.create(
            invoice=invoice,
            product=product,
            quantity=quantity,
            unit_price=unit_price,
            subtotal=subtotal
        )
        
        # Reduce stock
        inventory = product.inventory
        inventory.quantity -= quantity
        inventory.save()
        
        total += subtotal
    
    invoice.total = total
    invoice.save()
    
    return JsonResponse({
        'success': True,
        'invoice_number': invoice_number,
        'invoice_id': invoice.id,
        'total': float(total)
    })


# ============================================
# AUTHENTICATION VIEWS
# ============================================

from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm

def login_view(request):
    """User login view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            messages.success(request, f'مرحباً بك {user.get_full_name() or user.username}')
            return redirect('dashboard')
        else:
            messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة')
    
    return render(request, 'login.html')


def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, f'تم إنشاء الحساب بنجاح! مرحباً بك {user.username}')
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'register.html', {'form': form})


def logout_view(request):
    """User logout view"""
    auth_logout(request)
    messages.success(request, 'تم تسجيل الخروج بنجاح')
    return redirect('login')


def download_statement(request):
    """Download account statement as CSV"""
    import csv
    from django.http import HttpResponse
    from datetime import datetime
    
    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = f'attachment; filename="account_statement_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    # Add BOM for Excel UTF-8 support
    response.write('\ufeff')
    
    writer = csv.writer(response)
    # Write header
    writer.writerow(['رقم الفاتورة', 'العميل', 'التاريخ', 'الحالة', 'المبلغ'])
    
    # Get all invoices
    invoices = SaleInvoice.objects.select_related('customer').order_by('-issued_date')
    
    for invoice in invoices:
        writer.writerow([
            invoice.number,
            invoice.customer.name,
            invoice.issued_date.strftime('%Y-%m-%d'),
            invoice.get_status_display(),
            f"{invoice.total:.2f}"
        ])
    
    return response


def create_bulk_purchase(request):
    """Create bulk purchase orders for low stock items"""
    if request.method == 'POST':
        # Get all low stock items
        low_stock_items = InventoryItem.objects.filter(
            quantity__lte=F('reorder_level')
        ).select_related('product')
        
        if not low_stock_items.exists():
            messages.info(request, 'لا توجد منتجات تحتاج إلى إعادة طلب حالياً')
            return redirect('dashboard')
        
        # Get or create default supplier
        supplier, created = Supplier.objects.get_or_create(
            name='مورد افتراضي',
            defaults={'email': 'supplier@default.com', 'phone': '0000000000'}
        )
        
        # Create purchase order
        from datetime import date
        po_number = f'PO-{date.today().strftime("%Y%m%d")}-{PurchaseOrder.objects.count() + 1:04d}'
        
        purchase_order = PurchaseOrder.objects.create(
            number=po_number,
            supplier=supplier,
            issued_date=date.today(),
            status='draft',
            total=0
        )
        
        # Calculate total
        total = Decimal('0')
        for item in low_stock_items:
            # Calculate quantity needed (reorder_level - current quantity + buffer)
            needed = max(item.reorder_level - item.quantity + 10, 0)
            if needed > 0:
                subtotal = item.product.price * needed
                total += subtotal
        
        purchase_order.total = total
        purchase_order.save()
        
        messages.success(request, f'تم إنشاء أمر شراء مجمع #{purchase_order.number} بنجاح لـ {low_stock_items.count()} منتج')
        return redirect('purchases')
    
    # GET request - show confirmation page
    low_stock_items = InventoryItem.objects.filter(
        quantity__lte=F('reorder_level')
    ).select_related('product')
    
    context = {
        'low_stock_items': low_stock_items,
        'total_items': low_stock_items.count()
    }
    
    return render(request, 'bulk_purchase_confirm.html', context)


@login_required
def profile(request):
    """User profile page - shows user information and settings"""
    user = request.user
    
    # Handle password change
    if request.method == 'POST' and 'change_password' in request.POST:
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if not user.check_password(current_password):
            messages.error(request, 'كلمة المرور الحالية غير صحيحة')
        elif new_password != confirm_password:
            messages.error(request, 'كلمات المرور الجديدة غير متطابقة')
        elif len(new_password) < 8:
            messages.error(request, 'يجب أن تكون كلمة المرور 8 أحرف على الأقل')
        else:
            user.set_password(new_password)
            user.save()
            # Keep user logged in after password change
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, user)
            messages.success(request, 'تم تغيير كلمة المرور بنجاح')
            return redirect('profile')

    # Handle profile update
    if request.method == 'POST' and 'update_profile' in request.POST:
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        username = request.POST.get('username', '').strip()
        phone = request.POST.get('phone', '').strip()
        bio = request.POST.get('bio', '').strip()

        if username and username != user.username:
            if user.__class__.objects.filter(username=username).exclude(id=user.id).exists():
                messages.error(request, 'اسم المستخدم مستخدم بالفعل')
                return redirect('profile')
            user.username = username

        if email and email != user.email:
            if user.__class__.objects.filter(email=email).exclude(id=user.id).exists():
                messages.error(request, 'البريد الإلكتروني مستخدم بالفعل')
                return redirect('profile')
            user.email = email

        user.first_name = first_name
        user.last_name = last_name
        user.save()

        from .models import UserProfile
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        user_profile.phone = phone
        user_profile.bio = bio
        user_profile.save()

        messages.success(request, 'تم تحديث البيانات الشخصية بنجاح')
        return redirect('profile')
    
    try:
        from .models import UserProfile, Subscription
        user_profile = UserProfile.objects.get(user=user)
    except:
        from .models import UserProfile
        user_profile, created = UserProfile.objects.get_or_create(user=user)

    # Get active sessions
    from .models import UserSession
    current_session_key = request.session.session_key
    active_sessions = UserSession.objects.filter(user=user)

    # Mark current session
    if current_session_key:
        active_sessions.update(is_current=False)
        UserSession.objects.filter(session_key=current_session_key).update(is_current=True)
    
    # Get or create subscription
    try:
        from .models import Subscription
        subscription = Subscription.objects.get(user=user)
    except:
        from .models import Subscription
        from datetime import timedelta
        subscription = Subscription.objects.create(
            user=user,
            plan='free',
            renewal_date=timezone.now().date() + timedelta(days=365)
        )
    
    # Get user statistics
    invoices_count = SaleInvoice.objects.filter(created_at__year=timezone.now().year).count()
    total_sales = SaleInvoice.objects.filter(status='paid').aggregate(Sum('total'))['total__sum'] or 0
    
    # Subscription plans for upgrade
    plans = [
        {
            'name': 'الخطة الأساسية',
            'id': 'basic',
            'price': 49,
            'users': 5,
            'storage': 5,
            'features': ['تقارير أساسية', 'دعم بريد إلكتروني', 'نسخ احتياطي أسبوعي']
        },
        {
            'name': 'الخطة الاحترافية',
            'id': 'professional',
            'price': 149,
            'users': 50,
            'storage': 100,
            'features': ['تقارير متقدمة', 'دعم فني 24/7', 'نسخ احتياطي يومي', 'تكامل API']
        },
        {
            'name': 'خطة المؤسسات',
            'id': 'enterprise',
            'price': 499,
            'users': -1,
            'storage': -1,
            'features': ['كل المميزات', 'مدير حساب مخصص', 'SLA مضمون', 'تدريب فني']
        },
    ]
    
    context = {
        'user': user,
        'profile': user_profile,
        'subscription': subscription,
        'invoices_count': invoices_count,
        'total_sales': total_sales,
        'plans': plans,
        'active_sessions': active_sessions,
        'current_session_key': current_session_key,
    }
    
    return render(request, 'profile.html', context)


@login_required
def toggle_two_factor(request):
    """Enable/disable two-factor authentication"""
    from .models import UserProfile
    user = request.user
    profile = UserProfile.objects.get(user=user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'enable':
            import secrets
            # Generate a secret for 2FA
            secret = secrets.token_urlsafe(32)
            profile.two_factor_secret = secret
            profile.two_factor_enabled = True
            profile.save()
            messages.success(request, 'تم تفعيل المصادقة الثنائية بنجاح')
        elif action == 'disable':
            profile.two_factor_enabled = False
            profile.two_factor_secret = ''
            profile.save()
            messages.success(request, 'تم تعطيل المصادقة الثنائية')
    
    return redirect('profile')


@login_required
def upgrade_subscription(request, plan_id):
    """Upgrade user subscription to a new plan"""
    from .models import Subscription
    from datetime import timedelta
    
    user = request.user
    subscription = Subscription.objects.get(user=user)
    
    # Validate plan
    valid_plans = ['basic', 'professional', 'enterprise']
    if plan_id not in valid_plans:
        messages.error(request, 'خطة غير صحيحة')
        return redirect('profile')
    
    # Plan prices
    plan_prices = {
        'basic': 49,
        'professional': 149,
        'enterprise': 499,
    }
    
    subscription.plan = plan_id
    subscription.status = 'active'
    subscription.renewal_date = timezone.now().date() + timedelta(days=30)
    subscription.monthly_cost = plan_prices[plan_id]
    subscription.save()
    
    messages.success(request, f'تم ترقية اشتراكك إلى {subscription.get_plan_display()} بنجاح')
    return redirect('profile')


@login_required
def delete_account(request):
    """Delete user account permanently"""
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm = request.POST.get('confirm_delete')
        
        # Verify password
        if not request.user.check_password(password):
            messages.error(request, 'كلمة المرور غير صحيحة')
            return redirect('profile')
        
        if confirm != 'على_علم_تام':
            messages.error(request, 'يجب عليك تأكيد الحذف')
            return redirect('profile')
        
        user = request.user
        username = user.username
        
        # Delete user and related data
        user.delete()
        
        messages.success(request, f'تم حذف حسابك {username} بنجاح. وداعاً!')
        return redirect('login')
    
    return render(request, 'delete_account_confirm.html')


@login_required
def upload_avatar(request):
    """Upload user profile avatar"""
    if request.method == 'POST' and request.FILES.get('avatar'):
        user = request.user
        avatar_file = request.FILES['avatar']
        
        # Validate file size (max 5MB)
        if avatar_file.size > 5 * 1024 * 1024:
            return JsonResponse({'success': False, 'error': 'حجم الملف يجب أن يكون أقل من 5 MB'})
        
        # Validate file type
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if avatar_file.content_type not in allowed_types:
            return JsonResponse({'success': False, 'error': 'نوع الملف غير مدعوم. استخدم JPG أو PNG أو GIF'})
        
        try:
            # Get or create user profile
            from .models import UserProfile
            profile, created = UserProfile.objects.get_or_create(user=user)
            
            # Delete old avatar if exists
            if profile.avatar:
                old_path = profile.avatar.name
                if default_storage.exists(old_path):
                    default_storage.delete(old_path)
            
            # Save new avatar
            profile.avatar = avatar_file
            profile.save()
            
            return JsonResponse({
                'success': True,
                'message': 'تم تحديث الصورة بنجاح',
                'avatar_url': profile.avatar.url if profile.avatar else ''
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'لم يتم تحميل أي ملف'})


# ============================================
# SSO CONFIGURATION ENDPOINTS
# ============================================

def api_sso_config(request):
    """Get all SSO providers configuration"""
    from .sso_config import sso_manager
    
    providers_data = {}
    for provider_id, provider in sso_manager.get_all_providers().items():
        providers_data[provider_id] = {
            'name': provider.name,
            'is_enabled': provider.is_enabled,
            'config': provider.get_config(),
        }
    
    return JsonResponse({
        'providers': providers_data,
        'role_mappings': sso_manager.get_role_mapping()
    })


# ============================================
# NEW API ENDPOINTS FOR SETTINGS PAGES
# ============================================

@csrf_exempt
def api_save_general_settings(request):
    """API: Save general settings (company, taxes, templates)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        import json
        data = json.loads(request.body)
        
        settings_obj = CompanySettings.objects.first()
        if not settings_obj:
            settings_obj = CompanySettings.objects.create()

        vat_number = data.get('vatNumber') or data.get('vatId', '')
        default_tax_rate = data.get('vatRate', settings_obj.default_tax_rate)

        def to_bool(value, fallback=False):
            if value is None:
                return fallback
            if isinstance(value, bool):
                return value
            if isinstance(value, (int, float)):
                return bool(value)
            if isinstance(value, str):
                return value.strip().lower() in ['1', 'true', 'yes', 'on']
            return fallback

        tax_enabled = to_bool(data.get('taxEnabled'), settings_obj.tax_enabled)
        prices_include_tax = to_bool(data.get('pricesIncludeTax'), settings_obj.prices_include_tax)
        show_vat_on_invoice = to_bool(data.get('showVatOnInvoice'), settings_obj.show_vat_on_invoice)
        currency = data.get('currency', settings_obj.currency)
        default_print_template = data.get('templateSelected', settings_obj.default_print_template)

        settings_obj.company_name_ar = data.get('companyName', settings_obj.company_name_ar)
        settings_obj.company_name_en = data.get('companyNameEn', settings_obj.company_name_en)
        settings_obj.vat_number = vat_number or ''
        settings_obj.default_tax_rate = Decimal(str(default_tax_rate or 0))
        settings_obj.tax_enabled = tax_enabled
        settings_obj.prices_include_tax = prices_include_tax
        settings_obj.show_vat_on_invoice = show_vat_on_invoice
        settings_obj.currency = currency or settings_obj.currency
        if default_print_template in ['classic', 'modern', 'minimal']:
            settings_obj.default_print_template = default_print_template
        settings_obj.save()

        # Optional: Keep profile/session in sync when available
        if hasattr(request.user, 'profile'):
            profile = request.user.profile
            profile.company_name = settings_obj.company_name_ar
            profile.company_name_en = settings_obj.company_name_en
            profile.vat_id = settings_obj.vat_number
            profile.save()
        else:
            request.session['company_settings'] = {
                'company_name': settings_obj.company_name_ar,
                'company_name_en': settings_obj.company_name_en,
                'vat_id': settings_obj.vat_number,
            }
        
        return JsonResponse({
            'success': True,
            'message': 'تم حفظ إعدادات الشركة بنجاح ✓'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
def api_upload_company_logo(request):
    """API: Upload company logo"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        logo_file = request.FILES.get('logo')
        if not logo_file:
            return JsonResponse({'success': False, 'error': 'لم يتم تحميل ملف'})
        
        # Validate file size (max 2MB)
        if logo_file.size > 2 * 1024 * 1024:
            return JsonResponse({'success': False, 'error': 'حجم الملف يجب أن يكون أقل من 2 MB'})
        
        # Validate file type
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/svg+xml']
        if logo_file.content_type not in allowed_types:
            return JsonResponse({'success': False, 'error': 'نوع الملف غير مدعوم'})
        
        # Save logo to company settings
        settings_obj = CompanySettings.objects.first()
        if not settings_obj:
            settings_obj = CompanySettings.objects.create()

        if settings_obj.logo:
            old_path = settings_obj.logo.name
            if default_storage.exists(old_path):
                default_storage.delete(old_path)
        settings_obj.logo = logo_file
        settings_obj.save()
        logo_url = settings_obj.logo.url
        
        return JsonResponse({
            'success': True,
            'message': 'تم تحميل الشعار بنجاح ✓',
            'logo_url': logo_url
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
def api_delete_company_logo(request):
    """API: Delete company logo"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

    try:
        settings_obj = CompanySettings.objects.first()
        if settings_obj and settings_obj.logo:
            old_path = settings_obj.logo.name
            if default_storage.exists(old_path):
                default_storage.delete(old_path)
            settings_obj.logo = None
            settings_obj.save()

        return JsonResponse({
            'success': True,
            'message': 'تم حذف الشعار بنجاح ✓'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
def api_upload_company_seal(request):
    """API: Upload company seal"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

    try:
        seal_file = request.FILES.get('seal')
        if not seal_file:
            return JsonResponse({'success': False, 'error': 'لم يتم تحميل ملف'})

        # Validate file size (max 2MB)
        if seal_file.size > 2 * 1024 * 1024:
            return JsonResponse({'success': False, 'error': 'حجم الملف يجب أن يكون أقل من 2 MB'})

        # Validate file type
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/svg+xml']
        if seal_file.content_type not in allowed_types:
            return JsonResponse({'success': False, 'error': 'نوع الملف غير مدعوم'})

        settings_obj = CompanySettings.objects.first()
        if not settings_obj:
            settings_obj = CompanySettings.objects.create()

        if settings_obj.seal:
            old_path = settings_obj.seal.name
            if default_storage.exists(old_path):
                default_storage.delete(old_path)
        settings_obj.seal = seal_file
        settings_obj.save()

        return JsonResponse({
            'success': True,
            'message': 'تم تحميل الختم بنجاح ✓',
            'seal_url': settings_obj.seal.url
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
def api_save_locale_settings(request):
    """API: Save language and localization settings"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        import json
        data = json.loads(request.body)
        
        # Get or create user profile
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        # Update locale settings
        profile.system_language = data.get('systemLanguage', profile.system_language)
        profile.report_language = data.get('reportLanguage', profile.report_language)
        profile.timezone = data.get('timezoneSelect', profile.timezone)
        profile.use_24hour_format = data.get('format24Toggle', profile.use_24hour_format)
        profile.date_format = data.get('dateFormat', profile.date_format)
        profile.calendar_type = data.get('calendarType', profile.calendar_type)
        
        profile.save()
        
        return JsonResponse({
            'success': True,
            'message': 'تم حفظ إعدادات اللغة والتوقيت بنجاح ✓'
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@csrf_exempt
def api_get_company_info(request):
    """API endpoint to get company information"""
    try:
        settings_obj = CompanySettings.objects.first()
        if not settings_obj:
            settings_obj = CompanySettings.objects.create()
        
        return JsonResponse({
            'success': True,
            'company_name_ar': settings_obj.company_name_ar or 'شركتي',
            'company_name_en': settings_obj.company_name_en or 'My Company',
            'logo': settings_obj.logo.url if settings_obj.logo else None,
            'vat_number': settings_obj.vat_number or '',
            'currency': settings_obj.currency or 'SAR'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@csrf_exempt
def api_get_locale_settings(request):
    """API: Get current language and timezone settings"""
    try:
        locale_settings = request.session.get('locale_settings', {
            'system_language': 'ar',
            'report_language': 'ar',
            'timezone': 'UTC',
            'date_format': 'Y-m-d',
            'time_format': True,
            'calendar_type': 'gregorian',
        })
        
        return JsonResponse({
            'success': True,
            'settings': locale_settings
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
def api_save_2fa_setting(request):
    """API: Save 2FA preference"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        import json
        data = json.loads(request.body)
        
        # Save to user profile or session
        two_fa_enabled = data.get('enabled', False)
        
        if hasattr(request.user, 'profile'):
            profile = request.user.profile
            profile.two_factor_enabled = two_fa_enabled
            profile.save()
        
        request.session['two_fa_enabled'] = two_fa_enabled
        
        status_msg = 'تم تفعيل المصادقة الثنائية ✓' if two_fa_enabled else 'تم تعطيل المصادقة الثنائية'
        
        return JsonResponse({
            'success': True,
            'message': status_msg
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
def api_save_print_template_settings(request):
    """API: Save print template preferences"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        import json
        data = json.loads(request.body)

        template_name = data.get('template')  # 'classic', 'modern', or 'minimal'
        template_id = data.get('templateId')
        header_title = data.get('headerTitle')
        show_qr = data.get('showQR')
        show_signature = data.get('showSignature')
        show_tax_details = data.get('showTaxDetails')
        company_name_ar = data.get('companyNameAr')
        vat_number = data.get('vatNumber')

        print(f"DEBUG: Received template_name={template_name}, template_id={template_id}")

        # Update company settings
        settings_obj, created = CompanySettings.objects.get_or_create(id=1)
        
        # Save selected template name
        if template_name:
            settings_obj.default_print_template = template_name
            print(f"DEBUG: Setting default_print_template to {template_name}")
        
        if company_name_ar is not None:
            settings_obj.company_name_ar = company_name_ar
        if vat_number is not None:
            settings_obj.vat_number = vat_number
        
        settings_obj.save()
        print(f"DEBUG: Settings saved. Template is now: {settings_obj.default_print_template}")

        # Update selected template settings (for database templates)
        if template_id:
            template = PrintTemplate.objects.filter(id=template_id, template_type='sales_invoice').first()
            if template:
                if header_title is not None:
                    template.header_title = header_title
                if show_qr is not None:
                    template.show_qr_code = bool(show_qr)
                if show_signature is not None:
                    template.show_signature = bool(show_signature)
                if show_tax_details is not None:
                    template.show_vat = bool(show_tax_details)
                template.save()

                # Set as default
                PrintTemplate.objects.filter(template_type='sales_invoice').update(is_default=False)
                template.is_default = True
                template.save()

        return JsonResponse({
            'success': True,
            'message': 'تم حفظ إعدادات نماذج الطباعة بنجاح ✓',
            'saved_template': settings_obj.default_print_template
        })
    except Exception as e:
        print(f"DEBUG: Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
def api_mark_notification_read(request, notification_id):
    """API: Mark notification as read"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        notification = Notification.objects.get(id=notification_id)
        notification.is_read = True
        notification.save()
        
        return JsonResponse({
            'success': True,
            'message': 'تم تعليم الإشعار كمقروء',
            'notification_id': notification_id
        })
    except Notification.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'الإشعار غير موجود'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
def api_delete_notification(request, notification_id):
    """API: Delete notification"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        notification = Notification.objects.get(id=notification_id)
        notification.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'تم حذف الإشعار',
            'notification_id': notification_id
        })
    except Notification.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'الإشعار غير موجود'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
def api_save_notification_preferences(request):
    """API: Save notification channel preferences"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        import json
        data = json.loads(request.body)
        
        # Get or create company settings
        settings, _ = CompanySettings.objects.get_or_create(id=1)
        
        # Get existing preferences
        preferences = settings.notification_preferences or {}
        
        # Update preferences for specific event
        event_key = data.get('event', 'default')
        preferences[event_key] = {
            'in_app': data.get('in_app', True),
            'email': data.get('email', False),
            'sms': data.get('sms', False),
        }
        
        # Save to database
        settings.notification_preferences = preferences
        settings.save()
        
        return JsonResponse({
            'success': True,
            'message': 'تم حفظ تفضيلات التنبيهات',
            'preferences': preferences
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
def api_add_customer(request):
    """API: Add new customer (for Customer Management page)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        import json
        data = json.loads(request.body)
        
        customer = Customer.objects.create(
            name=data.get('name'),
            email=data.get('email'),
            phone=data.get('phone'),
            customer_type=data.get('type', 'individual'),
            is_active=True
        )
        
        return JsonResponse({
            'success': True,
            'message': f'تم إضافة العميل "{customer.name}" بنجاح ✓',
            'customer_id': customer.id
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
def api_delete_customer(request, customer_id):
    """API: Delete customer"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        customer = Customer.objects.get(id=customer_id)
        customer_name = customer.name
        customer.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'تم حذف العميل "{customer_name}" بنجاح ✓'
        })
    except Customer.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'العميل غير موجود'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def api_sso_enable(request, provider_id):
    """Enable an SSO provider"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'يجب استخدام POST'}, status=405)
    
    from .sso_config import sso_manager
    
    if sso_manager.enable_provider(provider_id):
        return JsonResponse({
            'success': True,
            'message': f'تم تفعيل {provider_id} بنجاح'
        })
    
    return JsonResponse({'success': False, 'error': 'مزود SSO غير موجود'})


def api_sso_disable(request, provider_id):
    """Disable an SSO provider"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'يجب استخدام POST'}, status=405)
    
    from .sso_config import sso_manager
    
    if sso_manager.disable_provider(provider_id):
        return JsonResponse({
            'success': True,
            'message': f'تم تعطيل {provider_id} بنجاح'
        })
    
    return JsonResponse({'success': False, 'error': 'مزود SSO غير موجود'})


def api_sso_configure(request, provider_id):
    """Configure SSO provider settings"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'يجب استخدام POST'}, status=405)
    
    import json
    from .sso_config import sso_manager
    
    try:
        data = json.loads(request.body)
        if sso_manager.configure_provider(provider_id, **data):
            return JsonResponse({
                'success': True,
                'message': f'تم تحديث إعدادات {provider_id} بنجاح'
            })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'فشل تحديث الإعدادات'})


def api_sso_map_role(request):
    """Map SSO group to Django role"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'يجب استخدام POST'}, status=405)
    
    import json
    from .sso_config import sso_manager
    
    try:
        data = json.loads(request.body)
        provider_id = data.get('provider_id')
        sso_group = data.get('sso_group')
        django_role = data.get('django_role')
        
        if sso_manager.map_sso_to_role(provider_id, sso_group, django_role):
            return JsonResponse({
                'success': True,
                'message': f'تم ربط المجموعة {sso_group} بالدور {django_role} بنجاح'
            })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'فشل ربط المجموعة'})


@login_required
@login_required
def api_sso_save(request):
    """Save SSO configuration to database"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'يجب استخدام POST'}, status=405)
    
    import json
    from .models import SSOConfiguration
    
    try:
        data = json.loads(request.body)
        
        # Save Google OAuth2 config
        if 'google' in data:
            google_config, created = SSOConfiguration.objects.get_or_create(provider='google')
            google_config.is_enabled = data['google'].get('is_enabled', False)
            google_config.google_client_id = data['google'].get('client_id', '')
            google_config.google_client_secret = data['google'].get('client_secret', '')
            google_config.updated_by = request.user
            google_config.save()
        
        # Save Microsoft Azure config
        if 'azure' in data:
            azure_config, created = SSOConfiguration.objects.get_or_create(provider='azure')
            azure_config.is_enabled = data['azure'].get('is_enabled', False)
            azure_config.azure_tenant_id = data['azure'].get('tenant_id', '')
            azure_config.azure_client_id = data['azure'].get('client_id', '')
            azure_config.azure_client_secret = data['azure'].get('client_secret', '')
            azure_config.updated_by = request.user
            azure_config.save()
        
        # Save SAML 2.0 config
        if 'saml2' in data:
            saml_config, created = SSOConfiguration.objects.get_or_create(provider='saml2')
            saml_config.is_enabled = data['saml2'].get('is_enabled', False)
            saml_config.saml_entity_id = data['saml2'].get('entity_id', '')
            saml_config.saml_sso_url = data['saml2'].get('sso_url', '')
            saml_config.saml_certificate = data['saml2'].get('certificate', '')
            saml_config.updated_by = request.user
            saml_config.save()
        
        # Save LDAP config
        if 'ldap' in data:
            ldap_config, created = SSOConfiguration.objects.get_or_create(provider='ldap')
            ldap_config.is_enabled = data['ldap'].get('is_enabled', False)
            ldap_config.ldap_server_uri = data['ldap'].get('server_uri', '')
            ldap_config.ldap_bind_dn = data['ldap'].get('bind_dn', '')
            ldap_config.ldap_bind_password = data['ldap'].get('bind_password', '')
            ldap_config.ldap_user_search_base = data['ldap'].get('user_search_base', '')
            ldap_config.updated_by = request.user
            ldap_config.save()
        
        # Log security event
        from .models import SecurityLog
        SecurityLog.objects.create(
            username=request.user.username,
            action_type='settings_change',
            description='تحديث إعدادات SSO',
            status='success',
            ip_address=get_client_ip(request)
        )
        
        return JsonResponse({
            'success': True,
            'message': 'تم حفظ إعدادات SSO بنجاح'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required  
def api_sso_load(request):
    """Load SSO configuration from database"""
    from .models import SSOConfiguration
    
    try:
        config_data = {}
        
        # Load Google config
        try:
            google = SSOConfiguration.objects.get(provider='google')
            config_data['google'] = {
                'is_enabled': google.is_enabled,
                'client_id': google.google_client_id,
                # Don't send client_secret to frontend for security
            }
        except SSOConfiguration.DoesNotExist:
            config_data['google'] = {'is_enabled': False, 'client_id': ''}
        
        # Load Azure config
        try:
            azure = SSOConfiguration.objects.get(provider='azure')
            config_data['azure'] = {
                'is_enabled': azure.is_enabled,
                'tenant_id': azure.azure_tenant_id,
                'client_id': azure.azure_client_id,
            }
        except SSOConfiguration.DoesNotExist:
            config_data['azure'] = {'is_enabled': False, 'tenant_id': '', 'client_id': ''}
        
        # Load SAML config
        try:
            saml = SSOConfiguration.objects.get(provider='saml2')
            config_data['saml2'] = {
                'is_enabled': saml.is_enabled,
                'entity_id': saml.saml_entity_id,
                'sso_url': saml.saml_sso_url,
            }
        except SSOConfiguration.DoesNotExist:
            config_data['saml2'] = {'is_enabled': False, 'entity_id': '', 'sso_url': ''}
        
        # Load LDAP config
        try:
            ldap = SSOConfiguration.objects.get(provider='ldap')
            config_data['ldap'] = {
                'is_enabled': ldap.is_enabled,
                'server_uri': ldap.ldap_server_uri,
                'bind_dn': ldap.ldap_bind_dn,
                'user_search_base': ldap.ldap_user_search_base,
            }
        except SSOConfiguration.DoesNotExist:
            config_data['ldap'] = {'is_enabled': False, 'server_uri': '', 'bind_dn': '', 'user_search_base': ''}
        
        return JsonResponse(config_data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def invoices_list(request):
    """List all invoices"""
    invoices = SaleInvoice.objects.all().order_by('-created_at')
    context = {
        'invoices': invoices,
        'page_title': 'الفواتير',
        'breadcrumbs': [
            {'title': 'الرئيسية', 'url': '/'},
            {'title': 'الفواتير', 'url': '/invoices/'},
        ]
    }
    return render(request, 'invoice_list.html', context)


def help_page(request):
    """Display help and documentation"""
    context = {
        'page_title': 'المساعدة والدليل',
        'help_sections': [
            {
                'title': 'دليل المستخدم المالي',
                'description': 'شرح شامل لإدارة الشؤون المالية والضرائب',
                'icon': 'description',
                'url': '/settings/general/'
            },
            {
                'title': 'إدارة الفواتير',
                'description': 'كيفية إنشاء وتعديل وإدارة الفواتير',
                'icon': 'receipt_long',
                'url': '/invoices/'
            },
            {
                'title': 'تقارير الإقرار الضريبي',
                'description': 'إنشاء تقارير ضريبية وإقرارات دورية',
                'icon': 'assessment',
                'url': '/reports/'
            },
            {
                'title': 'تكامل الجمارك',
                'description': 'ربط نظام الجمارك مع النظام الأساسي',
                'icon': 'import_export',
                'url': '/settings/system/'
            }
        ],
        'breadcrumbs': [
            {'title': 'الرئيسية', 'url': '/'},
            {'title': 'المساعدة', 'url': '/help/'},
        ]
    }
    return render(request, 'help.html', context)


def privacy_policy(request):
    """Privacy policy page"""
    return render(request, 'privacy_policy.html')


def terms_of_service(request):
    """Terms of service page"""
    return render(request, 'terms_of_service.html')


def support_page(request):
    """Support page"""
    return render(request, 'support.html')


def tax_settings_redirect(request):
    """Redirect legacy tax settings URL to taxes page"""
    return redirect('taxes')


def print_templates_settings_redirect(request):
    """Redirect legacy print templates settings URL to print templates page"""
    return redirect('print_templates')


def security_settings_redirect(request):
    """Redirect legacy security settings URL to security page"""
    return redirect('security')


@login_required
def terminate_session(request, session_id):
    """Terminate a specific user session"""
    from .models import UserSession
    from django.contrib.sessions.models import Session
    
    try:
        # Get the session for this user
        user_session = UserSession.objects.get(id=session_id, user=request.user)
        
        # Prevent terminating current session
        current_session_key = request.session.session_key
        if user_session.session_key == current_session_key:
            messages.error(request, 'لا يمكنك إنهاء الجلسة الحالية')
            return redirect('profile')
        
        # Delete the Django session
        try:
            session = Session.objects.get(session_key=user_session.session_key)
            session.delete()
        except Session.DoesNotExist:
            pass
        
        # Delete the UserSession record
        user_session.delete()
        
        messages.success(request, 'تم إنهاء الجلسة بنجاح')
    except UserSession.DoesNotExist:
        messages.error(request, 'الجلسة غير موجودة')
    
    return redirect('profile')


@login_required
def terminate_all_sessions(request):
    """Terminate all sessions except the current one"""
    from .models import UserSession
    from django.contrib.sessions.models import Session
    
    current_session_key = request.session.session_key
    
    # Get all sessions except current
    other_sessions = UserSession.objects.filter(user=request.user).exclude(session_key=current_session_key)
    
    count = 0
    for user_session in other_sessions:
        # Delete Django session
        try:
            session = Session.objects.get(session_key=user_session.session_key)
            session.delete()
        except Session.DoesNotExist:
            pass
        
        # Delete UserSession record
        user_session.delete()
        count += 1
    
    if count > 0:
        messages.success(request, f'تم إنهاء {count} جلسة بنجاح')
    else:
        messages.info(request, 'لا توجد جلسات أخرى لإنهائها')
    
    return redirect('profile')


def api_search_notifications(request):
    """API: Search notifications by title or message"""
    if request.method != 'GET':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        query = request.GET.get('q', '').strip()
        
        if not query or len(query) < 2:
            return JsonResponse({
                'success': True,
                'results': [],
                'count': 0
            })
        
        from django.db.models import Q
        notifications = Notification.objects.filter(
            Q(title__icontains=query) | 
            Q(message__icontains=query)
        ).order_by('-created_at')[:50]
        
        results = []
        for notif in notifications:
            results.append({
                'id': notif.id,
                'title': notif.title,
                'message': notif.message,
                'level': notif.level,
                'is_read': notif.is_read,
                'created_at': notif.created_at.isoformat(),
            })
        
        return JsonResponse({
            'success': True,
            'results': results,
            'count': len(results)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def api_get_storage_info(request):
    """API: Get storage information"""
    if request.method != 'GET':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        settings = CompanySettings.objects.first()
        
        if not settings:
            settings, _ = CompanySettings.objects.get_or_create(id=1)
        
        storage_used = float(settings.storage_used_mb or 0)
        storage_quota = float(settings.storage_quota_mb or 10240)
        
        percentage = (storage_used / storage_quota * 100) if storage_quota > 0 else 0
        
        return JsonResponse({
            'success': True,
            'storage_used_mb': storage_used,
            'storage_used_gb': round(storage_used / 1024, 2),
            'storage_quota_mb': storage_quota,
            'storage_quota_gb': round(storage_quota / 1024, 2),
            'percentage': round(percentage, 1),
            'remaining_gb': round((storage_quota - storage_used) / 1024, 2)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
def api_get_current_user(request):
    """Get current user information"""
    user = request.user
    return JsonResponse({
        'success': True,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'full_name': f"{user.first_name} {user.last_name}".strip() or user.username,
    })


@login_required
def api_get_security_status(request):
    """Get overall security status"""
    from django.contrib.auth.models import User
    from .models import UserProfile
    
    total_users = User.objects.count()
    two_fa_enabled = UserProfile.objects.filter(two_factor_enabled=True).count()
    
    # Calculate percentage
    percentage = int((two_fa_enabled / total_users * 100)) if total_users > 0 else 0
    
    # Ensure within 0-100 range
    percentage = max(0, min(100, percentage))
    
    return JsonResponse({
        'success': True,
        'total_users': total_users,
        'two_fa_enabled': two_fa_enabled,
        'percentage': percentage,
    })