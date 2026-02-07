from django.contrib import admin

from . import models


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "is_active", "created_at")
    search_fields = ("name",)
    list_filter = ("is_active", "parent")


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "customer_type", "email", "phone", "balance", "is_active")
    search_fields = ("name", "email", "phone")
    list_filter = ("customer_type", "is_active")


@admin.register(models.Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "is_active")
    search_fields = ("name", "email", "phone")
    list_filter = ("is_active",)


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "category", "price", "is_active")
    search_fields = ("name", "sku", "category")
    list_filter = ("category", "is_active")


@admin.register(models.InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ("product", "quantity", "reorder_level", "updated_at")
    search_fields = ("product__name", "product__sku")


@admin.register(models.SaleInvoice)
class SaleInvoiceAdmin(admin.ModelAdmin):
    list_display = ("number", "customer", "issued_date", "status", "total")
    search_fields = ("number", "customer__name")
    list_filter = ("status", "issued_date")


@admin.register(models.SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ("invoice", "product", "quantity", "unit_price", "subtotal")


@admin.register(models.PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ("number", "supplier", "issued_date", "status", "total")
    search_fields = ("number", "supplier__name")
    list_filter = ("status", "issued_date")


@admin.register(models.TaxRate)
class TaxRateAdmin(admin.ModelAdmin):
    list_display = ("name", "rate", "is_default")
    list_filter = ("is_default",)


@admin.register(models.Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "level", "is_read", "created_at")
    list_filter = ("level", "is_read")
    search_fields = ("title", "message")


@admin.register(models.Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "capacity", "status", "is_active", "created_at")
    search_fields = ("name", "location")
    list_filter = ("status", "is_active")


@admin.register(models.CompanySettings)
class CompanySettingsAdmin(admin.ModelAdmin):
    list_display = ("company_name_ar", "company_name_en", "currency", "timezone", "tax_enabled")
    readonly_fields = ("updated_at",)


@admin.register(models.SecurityLog)
class SecurityLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "username", "action_type", "status", "ip_address", "device_type")
    list_filter = ("action_type", "status", "timestamp")
    search_fields = ("username", "description", "ip_address")
    readonly_fields = ("timestamp",)
    ordering = ("-timestamp",)


@admin.register(models.SSOConfiguration)
class SSOConfigurationAdmin(admin.ModelAdmin):
    list_display = ("provider", "is_enabled", "updated_at", "updated_by")
    list_filter = ("provider", "is_enabled")
    readonly_fields = ("created_at", "updated_at", "updated_by")
    ordering = ("provider",)
    
    fieldsets = (
        ('معلومات أساسية', {
            'fields': ('provider', 'is_enabled')
        }),
        ('Google OAuth2', {
            'fields': ('google_client_id', 'google_client_secret'),
            'classes': ('collapse',)
        }),
        ('Microsoft Azure AD', {
            'fields': ('azure_tenant_id', 'azure_client_id', 'azure_client_secret'),
            'classes': ('collapse',)
        }),
        ('SAML 2.0', {
            'fields': ('saml_entity_id', 'saml_sso_url', 'saml_certificate'),
            'classes': ('collapse',)
        }),
        ('LDAP/Active Directory', {
            'fields': ('ldap_server_uri', 'ldap_bind_dn', 'ldap_bind_password', 'ldap_user_search_base', 'ldap_group_search_base'),
            'classes': ('collapse',)
        }),
        ('معلومات إضافية', {
            'fields': ('role_mapping', 'created_at', 'updated_at', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.updated_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
