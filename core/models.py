from django.db import models
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self) -> str:
        return self.name


class Customer(models.Model):
    TYPE_INDIVIDUAL = "individual"
    TYPE_COMPANY = "company"
    TYPE_CHOICES = [
        (TYPE_INDIVIDUAL, "Individual"),
        (TYPE_COMPANY, "Company"),
    ]

    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    customer_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_COMPANY)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name


class Supplier(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, null=True, blank=True, related_name='products')
    price = models.DecimalField(max_digits=12, decimal_places=2)
    sale_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    note = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.sku})"
    
    def get_display_price(self):
        """Return sale price if available, otherwise regular price"""
        return self.sale_price if self.sale_price else self.price


class InventoryItem(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="inventory")
    quantity = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=10)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.product.name} - {self.quantity}"


class PrintTemplate(models.Model):
    """Store print template configurations for invoices and documents"""
    TEMPLATE_TYPE_CHOICES = [
        ('sales_invoice', 'قالب فاتورة المبيعات'),
        ('purchase_order', 'قالب أمر الشراء'),
        ('inventory_report', 'قالب تقرير المخزون'),
        ('customer_statement', 'قالب بيان العميل'),
    ]
    
    TEMPLATE_STYLE_CHOICES = [
        ('standard', 'نموذج قياسي (A4)'),
        ('thermal', 'حراري / نقاط بيع'),
        ('minimal', 'نموذج عصري (مبسط)'),
    ]
    
    name = models.CharField(max_length=255)
    template_type = models.CharField(max_length=50, choices=TEMPLATE_TYPE_CHOICES)
    style = models.CharField(max_length=50, choices=TEMPLATE_STYLE_CHOICES, default='standard')
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    show_qr_code = models.BooleanField(default=True)
    show_signature = models.BooleanField(default=True)
    show_vat = models.BooleanField(default=True)
    header_title = models.CharField(max_length=255, default='فاتورة ضريبية')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'نموذج الطباعة'
        verbose_name_plural = 'نماذج الطباعة'
    
    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"


class SaleInvoice(models.Model):
    STATUS_PAID = "paid"
    STATUS_PENDING = "pending"
    STATUS_OVERDUE = "overdue"
    STATUS_CHOICES = [
        (STATUS_PAID, "Paid"),
        (STATUS_PENDING, "Pending"),
        (STATUS_OVERDUE, "Overdue"),
    ]

    number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="invoices")
    issued_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True, help_text="ملاحظات الفاتورة - تظهر في أسفل الفاتورة")
    print_template = models.ForeignKey(PrintTemplate, on_delete=models.SET_NULL, null=True, blank=True, related_name='sale_invoices', limit_choices_to={'template_type': 'sales_invoice'})
    includes_vat = models.BooleanField(default=True, help_text="هل الأسعار تشمل ضريبة القيمة المضافة")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.number
    
    def get_subtotal(self):
        """Calculate subtotal from all items"""
        total = sum(item.subtotal for item in self.items.all())
        return total or Decimal('0')
    
    def get_vat_amount(self):
        """Calculate VAT based on settings and includes_vat flag"""
        from decimal import Decimal
        try:
            settings = CompanySettings.objects.first()
            if not settings or not settings.tax_enabled:
                return Decimal('0')
            
            subtotal = self.get_subtotal()
            vat_rate = settings.default_tax_rate / Decimal('100')
            
            if self.includes_vat:
                # VAT is already included in the prices
                return subtotal - (subtotal / (1 + vat_rate))
            else:
                # Calculate VAT on top of subtotal
                return subtotal * vat_rate
        except Exception:
            return Decimal('0')
    
    def get_total(self):
        """Calculate total including or excluding VAT based on settings"""
        from decimal import Decimal
        subtotal = self.get_subtotal()
        vat = self.get_vat_amount()
        
        if self.includes_vat:
            return subtotal  # VAT already included
        else:
            return subtotal + vat  # Add VAT to subtotal


class SaleItem(models.Model):
    invoice = models.ForeignKey(SaleInvoice, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self) -> str:
        return f"{self.invoice.number} - {self.product.name}"


class PurchaseOrder(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_SENT = "sent"
    STATUS_RECEIVED = "received"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_SENT, "Sent"),
        (STATUS_RECEIVED, "Received"),
    ]

    number = models.CharField(max_length=50, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name="purchase_orders")
    issued_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True, help_text="ملاحظات أمر الشراء")
    print_template = models.ForeignKey(PrintTemplate, on_delete=models.SET_NULL, null=True, blank=True, related_name='purchase_orders', limit_choices_to={'template_type': 'purchase_order'})
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.number


class TaxRate(models.Model):
    name = models.CharField(max_length=120)
    rate = models.DecimalField(max_digits=5, decimal_places=2)
    is_default = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.name} ({self.rate}%)"


class Notification(models.Model):
    LEVEL_INFO = "info"
    LEVEL_WARNING = "warning"
    LEVEL_CRITICAL = "critical"
    LEVEL_CHOICES = [
        (LEVEL_INFO, "Info"),
        (LEVEL_WARNING, "Warning"),
        (LEVEL_CRITICAL, "Critical"),
    ]

    title = models.CharField(max_length=200)
    message = models.TextField()
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default=LEVEL_INFO)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.title


class UserProfile(models.Model):
    LANGUAGE_CHOICES = [
        ('ar', 'العربية (الأصلية)'),
        ('en', 'English (US)'),
        ('fr', 'Français'),
    ]
    
    REPORT_LANGUAGE_CHOICES = [
        ('ar', 'العربية'),
        ('en', 'English'),
        ('dual', 'ثنائي اللغة (Ar/En)'),
    ]
    
    TIMEZONE_CHOICES = [
        ('riyadh', '(GMT+03:00) الرياض، السعودية'),
        ('dubai', '(GMT+04:00) دبي، الإمارات'),
        ('cairo', '(GMT+02:00) القاهرة، مصر'),
    ]
    
    DATE_FORMAT_CHOICES = [
        ('dmy', 'DD/MM/YYYY'),
        ('mdy', 'MM/DD/YYYY'),
        ('ymd', 'YYYY-MM-DD'),
    ]
    
    CALENDAR_TYPE_CHOICES = [
        ('gregorian', 'ميلادي (Gregorian)'),
        ('hijri', 'هجري (Hijri)'),
        ('both', 'كلاهما'),
    ]
    
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    bio = models.TextField(blank=True)
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=255, blank=True)
    
    # Language and Localization Settings
    system_language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='ar')
    report_language = models.CharField(max_length=10, choices=REPORT_LANGUAGE_CHOICES, default='ar')
    timezone = models.CharField(max_length=50, choices=TIMEZONE_CHOICES, default='riyadh')
    use_24hour_format = models.BooleanField(default=True)
    date_format = models.CharField(max_length=10, choices=DATE_FORMAT_CHOICES, default='dmy')
    calendar_type = models.CharField(max_length=20, choices=CALENDAR_TYPE_CHOICES, default='gregorian')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Profile of {self.user.username}"


class Subscription(models.Model):
    PLAN_FREE = "free"
    PLAN_BASIC = "basic"
    PLAN_PROFESSIONAL = "professional"
    PLAN_ENTERPRISE = "enterprise"
    PLAN_CHOICES = [
        (PLAN_FREE, "الخطة المجانية"),
        (PLAN_BASIC, "الخطة الأساسية"),
        (PLAN_PROFESSIONAL, "الخطة الاحترافية"),
        (PLAN_ENTERPRISE, "خطة المؤسسات"),
    ]

    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='subscription')
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default=PLAN_FREE)
    status = models.CharField(max_length=20, default='active')
    start_date = models.DateField(auto_now_add=True)
    renewal_date = models.DateField(null=True, blank=True)
    monthly_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    storage_used = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    storage_total = models.DecimalField(max_digits=10, decimal_places=2, default=5)
    auto_renew = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.user.username} - {self.get_plan_display()}"

    def storage_percent(self):
        """Calculate storage usage percentage"""
        if self.storage_total == 0:
            return 0
        return int((self.storage_used / self.storage_total) * 100)

    def is_expired(self):
        """Check if subscription is expired"""
        return timezone.now().date() > self.renewal_date


class UserSession(models.Model):
    """Track active user sessions"""
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='active_sessions')
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    device_type = models.CharField(max_length=50, blank=True)
    browser = models.CharField(max_length=100, blank=True)
    os = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=200, blank=True)
    is_current = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-last_activity']

    def __str__(self):
        return f"{self.user.username} - {self.device_type} - {self.ip_address}"

    def get_device_info(self):
        """Get formatted device information"""
        if self.device_type and self.os:
            return f"{self.device_type} • {self.os}"
        return self.user_agent[:50] if self.user_agent else "Unknown Device"

    def get_browser_info(self):
        """Get formatted browser information"""
        return self.browser if self.browser else "Unknown Browser"

    def time_since_activity(self):
        """Get human readable time since last activity"""
        from django.utils.timesince import timesince
        if self.is_current:
            return "الآن"
        return f"منذ {timesince(self.last_activity, timezone.now())}"


class SecurityLog(models.Model):
    """Track security events and audit trail"""
    ACTION_TYPES = (
        ('login_success', 'دخول ناجح'),
        ('login_failed', 'محاولة دخول فاشلة'),
        ('logout', 'تسجيل خروج'),
        ('permission_change', 'تغيير صلاحيات'),
        ('settings_change', 'تغيير إعدادات'),
        ('role_change', 'تغيير الدور'),
        ('user_created', 'إنشاء مستخدم'),
        ('user_deleted', 'حذف مستخدم'),
        ('data_export', 'تصدير بيانات'),
        ('password_change', 'تغيير كلمة المرور'),
        ('2fa_enabled', 'تفعيل أمان'),
        ('suspicious_activity', 'نشاط مشبوه'),
        ('multiple_failed', 'فشل متعدد'),
    )
    
    STATUS_CHOICES = (
        ('success', 'نجح'),
        ('warning', 'تحذير'),
        ('failed', 'فشل'),
    )
    
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='security_logs')
    username = models.CharField(max_length=150, blank=True)  # Store username even if user is deleted
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    device_type = models.CharField(max_length=50, blank=True)
    browser = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='success')
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'سجل أمان'
        verbose_name_plural = 'سجلات الأمان'
    
    def __str__(self):
        return f"{self.get_action_type_display()} - {self.username} - {self.timestamp}"


class CompanySettings(models.Model):
    """Singleton model for company settings"""
    company_name_ar = models.CharField(max_length=255, blank=True)
    company_name_en = models.CharField(max_length=255, blank=True)
    currency = models.CharField(max_length=20, default="SAR")
    timezone = models.CharField(max_length=50, default="Asia/Riyadh")
    logo = models.ImageField(upload_to="company/", null=True, blank=True)
    seal = models.ImageField(upload_to="company/seals/", null=True, blank=True)

    tax_enabled = models.BooleanField(default=True)
    vat_number = models.CharField(max_length=50, blank=True)
    default_tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=15)
    prices_include_tax = models.BooleanField(default=True)
    show_vat_on_invoice = models.BooleanField(default=True)
    
    default_print_template = models.CharField(
        max_length=50, 
        default="classic", 
        choices=[
            ('classic', 'النموذج الكلاسيكي'),
            ('modern', 'النموذج العصري'),
            ('minimal', 'النموذج المبسط'),
        ]
    )
    
    # Notification preferences stored as JSON
    notification_preferences = models.JSONField(default=dict, blank=True)
    storage_used_mb = models.FloatField(default=0)  # Storage used in MB
    storage_quota_mb = models.FloatField(default=10240)  # 10GB default quota

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "إعدادات الشركة"
        verbose_name_plural = "إعدادات الشركة"

    def __str__(self):
        return self.company_name_ar or "Company Settings"


class Warehouse(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_INACTIVE = "inactive"
    STATUS_MAINTENANCE = "maintenance"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "نشط"),
        (STATUS_INACTIVE, "غير نشط"),
        (STATUS_MAINTENANCE, "صيانة"),
    ]

    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    capacity = models.DecimalField(max_digits=10, decimal_places=2, help_text="Capacity in percentage")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.name} - {self.location}"

    def get_capacity_status(self):
        """Return capacity status based on percentage"""
        if self.capacity >= 80:
            return 'high'
        elif self.capacity >= 50:
            return 'medium'
        else:
            return 'low'

class Module(models.Model):
    """System modules/sections for permission management"""
    name_ar = models.CharField(max_length=255)  # Arabic name
    name_en = models.CharField(max_length=255)  # English name
    description_ar = models.TextField()
    description_en = models.TextField()
    icon = models.CharField(max_length=100, default='dashboard')  # Material Symbol icon name
    color = models.CharField(max_length=20, default='blue')  # Color class (blue, green, orange, purple)
    order = models.IntegerField(default=0)  # Sort order
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'وحدة برمجية'
        verbose_name_plural = 'وحدات برمجية'

    def __str__(self):
        return f"{self.name_ar} ({self.name_en})"


class RolePermission(models.Model):
    """Detailed permissions for roles"""
    ACTION_CHOICES = [
        ('view', 'عرض'),
        ('add', 'إضافة'),
        ('change', 'تعديل'),
        ('delete', 'حذف'),
        ('export', 'تصدير'),
    ]
    
    group = models.ForeignKey('auth.Group', on_delete=models.CASCADE, related_name='role_permissions')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='permissions')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    is_allowed = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('group', 'module', 'action')
        ordering = ['module__order', 'action']
        verbose_name = 'صلاحية الدور'
        verbose_name_plural = 'صلاحيات الأدوار'

    def __str__(self):
        return f"{self.group.name} - {self.module.name_ar} - {self.get_action_display()}"


class SSOConfiguration(models.Model):
    """SSO Provider Configuration for Single Sign-On"""
    PROVIDER_CHOICES = [
        ('google', 'Google OAuth2'),
        ('azure', 'Microsoft Azure AD'),
        ('saml2', 'SAML 2.0'),
        ('ldap', 'LDAP/Active Directory'),
    ]
    
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES, unique=True)
    is_enabled = models.BooleanField(default=False)
    
    # Google OAuth2 Configuration
    google_client_id = models.CharField(max_length=255, blank=True)
    google_client_secret = models.CharField(max_length=255, blank=True)
    
    # Microsoft Azure AD Configuration
    azure_tenant_id = models.CharField(max_length=255, blank=True)
    azure_client_id = models.CharField(max_length=255, blank=True)
    azure_client_secret = models.CharField(max_length=255, blank=True)
    
    # SAML 2.0 Configuration
    saml_entity_id = models.CharField(max_length=500, blank=True)
    saml_sso_url = models.URLField(blank=True)
    saml_certificate = models.TextField(blank=True)
    
    # LDAP Configuration
    ldap_server_uri = models.CharField(max_length=500, blank=True)
    ldap_bind_dn = models.CharField(max_length=500, blank=True)
    ldap_bind_password = models.CharField(max_length=255, blank=True)
    ldap_user_search_base = models.CharField(max_length=500, blank=True)
    ldap_group_search_base = models.CharField(max_length=500, blank=True)
    
    # Role Mapping (JSON format)
    role_mapping = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['provider']
        verbose_name = 'إعدادات SSO'
        verbose_name_plural = 'إعدادات SSO'

    def __str__(self):
        status = 'مفعل' if self.is_enabled else 'معطل'
        return f"{self.get_provider_display()} - {status}"