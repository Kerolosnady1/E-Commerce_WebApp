"""
Forms for ERP System
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Category, Customer, InventoryItem, Notification, Product, PurchaseOrder, SaleInvoice, Supplier, TaxRate, Warehouse


class CategoryForm(forms.ModelForm):
    """Form for creating/editing categories"""
    class Meta:
        model = Category
        fields = ['name', 'parent', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم الفئة'}),
            'parent': forms.Select(attrs={'class': 'form-control'}),
        }


class CustomerForm(forms.ModelForm):
    """Form for creating/editing customers"""
    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone', 'customer_type', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم العميل'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'البريد الإلكتروني'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'رقم الهاتف'}),
            'customer_type': forms.Select(attrs={'class': 'form-control'}),
        }


class SupplierForm(forms.ModelForm):
    """Form for creating/editing suppliers"""
    class Meta:
        model = Supplier
        fields = ['name', 'email', 'phone', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم المورد'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'البريد الإلكتروني'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'رقم الهاتف'}),
        }


class ProductForm(forms.ModelForm):
    """Form for creating/editing products"""
    quantity = forms.IntegerField(
        required=False,
        initial=0,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'الكمية المتاحة',
            'min': '0'
        })
    )
    
    class Meta:
        model = Product
        fields = ['name', 'sku', 'category', 'price', 'sale_price', 'image', 'note', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم المنتج'}),
            'sku': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'رمز المنتج'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'السعر', 'step': '0.01'}),
            'sale_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'سعر التخفيض (اختياري)', 'step': '0.01'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'ملاحظات', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }


class InventoryItemForm(forms.ModelForm):
    """Form for managing inventory"""
    class Meta:
        model = InventoryItem
        fields = ['quantity', 'reorder_level']
        widgets = {
            'quantity': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 rounded-lg border bg-slate-700 border-slate-600 text-slate-100 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all',
                'placeholder': 'الكمية'
            }),
            'reorder_level': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 rounded-lg border bg-slate-700 border-slate-600 text-slate-100 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all',
                'placeholder': 'حد إعادة الطلب'
            }),
        }


class SaleInvoiceForm(forms.ModelForm):
    """Form for creating sales invoices"""
    class Meta:
        model = SaleInvoice
        fields = ['customer', 'issued_date', 'status', 'number', 'notes', 'print_template', 'includes_vat']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'issued_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'رقم الفاتورة'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'ملاحظات الفاتورة', 'rows': 3}),
            'print_template': forms.Select(attrs={'class': 'form-control'}),
            'includes_vat': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PurchaseOrderForm(forms.ModelForm):
    """Form for creating purchase orders"""
    class Meta:
        model = PurchaseOrder
        fields = ['supplier', 'issued_date', 'status', 'number', 'total', 'notes', 'print_template']
        widgets = {
            'supplier': forms.Select(attrs={'class': 'form-control'}),
            'issued_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'رقم الطلب'}),
            'total': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'المبلغ الإجمالي', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'ملاحظات أمر الشراء', 'rows': 3}),
            'print_template': forms.Select(attrs={'class': 'form-control'}),
        }


class TaxRateForm(forms.ModelForm):
    """Form for managing tax rates"""
    class Meta:
        model = TaxRate
        fields = ['name', 'rate', 'is_default']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم الضريبة'}),
            'rate': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'النسبة %', 'step': '0.01'}),
        }


class NotificationForm(forms.ModelForm):
    """Form for creating notifications"""
    class Meta:
        model = Notification
        fields = ['title', 'message', 'level']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'العنوان'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'الرسالة'}),
            'level': forms.Select(attrs={'class': 'form-control'}),
        }


class WarehouseForm(forms.ModelForm):
    """Form for creating/editing warehouses"""
    class Meta:
        model = Warehouse
        fields = ['name', 'location', 'capacity', 'status', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم المستودع'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'الموقع'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'السعة %', 'step': '0.01', 'min': '0', 'max': '100'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'الوصف (اختياري)'}),
        }


class UserRegistrationForm(UserCreationForm):
    """Form for creating new users"""
    email = forms.EmailField(
        required=True, 
        widget=forms.EmailInput(attrs={
            'class': 'w-full bg-slate-700 border border-slate-600 text-white rounded-xl px-4 py-3',
            'placeholder': 'example@domain.com'
        })
    )
    first_name = forms.CharField(
        max_length=100, 
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-slate-700 border border-slate-600 text-white rounded-xl px-4 py-3',
            'placeholder': 'الاسم الأول'
        })
    )
    last_name = forms.CharField(
        max_length=100, 
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-slate-700 border border-slate-600 text-white rounded-xl px-4 py-3',
            'placeholder': 'الاسم الأخير'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full bg-slate-700 border border-slate-600 text-white rounded-xl px-4 py-3',
                'placeholder': 'اسم المستخدم'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'w-full bg-slate-700 border border-slate-600 text-white rounded-xl px-4 py-3',
            'placeholder': '••••••••'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'w-full bg-slate-700 border border-slate-600 text-white rounded-xl px-4 py-3',
            'placeholder': '••••••••'
        })


class DateRangeForm(forms.Form):
    """Form for filtering by date range"""
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=False,
        label='من تاريخ'
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=False,
        label='إلى تاريخ'
    )
