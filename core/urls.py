from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    # Main Pages
    path("", views.dashboard, name="dashboard"),
    path("dashboard/", views.dashboard, name="dashboard_alt"),
    path("sales/", views.sales, name="sales"),
    path("customers/", views.customers, name="customers"),
    path("reports/", views.reports, name="reports"),
    path("settings/", RedirectView.as_view(url="/settings/general/"), name="settings_root"),
    path("settings/general/", views.general_settings, name="general_settings"),
    path("settings/system/", views.system_settings, name="system_settings"),
    path("settings/tax/", views.tax_settings_redirect, name="tax_settings_redirect"),
    path("settings/print-templates/", views.print_templates_settings_redirect, name="print_templates_settings_redirect"),
    path("settings/security/", views.security_settings_redirect, name="security_settings_redirect"),
    path("accounts/", views.accounts, name="accounts"),
    path("inventory/", views.inventory, name="inventory"),
    path("warehouses/", views.warehouses, name="warehouses"),
    path("purchases/", views.purchases, name="purchases"),
    path("purchases/search/", views.purchase_search, name="purchase_search"),
    path("purchases/export/", views.purchase_export, name="purchase_export"),
    path("purchases/new/", views.purchase_form, name="purchase_form"),
    path("suppliers/quick-create/", views.supplier_quick_create, name="supplier_quick_create"),
    path("taxes/", views.taxes, name="taxes"),
    path("print-templates/", views.print_templates, name="print_templates"),
    path("notifications/", views.notifications, name="notifications"),
    path("security/", views.security, name="security"),
    path("security/2fa/", views.security_2fa, name="security_2fa"),
    path("security/password-policy/", views.security_password_policy, name="security_password_policy"),
    path("security/add-role/", views.add_role, name="add_role"),
    path("security/delete-role/", views.delete_role, name="delete_role"),
    path("security/role-permissions/<str:role_name>/", views.get_role_permissions, name="get_role_permissions"),
    path("security/update-permissions/", views.update_role_permissions, name="update_role_permissions"),
    path("security/logs/", views.security_logs, name="security_logs"),
    path("locale-time/", views.locale_time, name="locale_time"),
    path("users-permissions/", views.users_permissions, name="users_permissions"),
    path("employees/", views.employees, name="employees"),
    path("pages/", views.pages_index, name="pages_index"),
    
    # Customer CRUD
    path("customers/create/", views.customer_create, name="customer_create"),
    path("customers/<int:pk>/edit/", views.customer_edit, name="customer_edit"),
    path("customers/<int:pk>/delete/", views.customer_delete, name="customer_delete"),
    
    # Product & Inventory CRUD
    path("products/create/", views.product_create, name="product_create"),
    path("products/<int:pk>/edit/", views.product_edit, name="product_edit"),
    path("inventory/<int:pk>/update/", views.inventory_update, name="inventory_update"),
    
    # Invoice CRUD
    path("invoices/create/", views.invoice_create, name="invoice_create"),
    path("invoices/<int:pk>/edit/", views.invoice_edit, name="invoice_edit"),
    path("invoices/<int:pk>/", views.invoice_detail, name="invoice_detail"),
    
    # Purchase Order CRUD
    path("purchase-orders/", views.purchases, name="purchase_orders_list"),
    path("purchase-orders/create/", views.purchase_order_create, name="purchase_order_create"),
    path("purchase-orders/<int:pk>/", views.purchase_order_detail, name="purchase_order_detail"),
    path("purchase-orders/<int:pk>/edit/", views.purchase_order_edit, name="purchase_order_edit"),
    
    # API Endpoints
    path("api/summary/", views.api_summary, name="api_summary"),
    path("api/alerts/", views.api_alerts, name="api_alerts"),
    path("api/customers/", views.api_customer_list, name="api_customer_list"),
    path("api/products/", views.api_product_list, name="api_product_list"),
    path("api/inventory/status/", views.api_inventory_status, name="api_inventory_status"),
    path("api/sales/stats/", views.api_sales_stats, name="api_sales_stats"),
    path("api/dashboard/", views.api_dashboard_data, name="api_dashboard_data"),
    path("api/search-products/", views.api_search_products, name="api_search_products"),
    path("api/submit-invoice/", views.api_submit_invoice, name="api_submit_invoice"),
    
    # New Settings API Endpoints
    path("api/settings/general/save/", views.api_save_general_settings, name="api_save_general_settings"),
    path("api/settings/logo/upload/", views.api_upload_company_logo, name="api_upload_company_logo"),
    path("api/settings/logo/delete/", views.api_delete_company_logo, name="api_delete_company_logo"),
    path("api/settings/seal/upload/", views.api_upload_company_seal, name="api_upload_company_seal"),
    path("api/settings/locale/save/", views.api_save_locale_settings, name="api_save_locale_settings"),
    path("api/settings/locale/get/", views.api_get_locale_settings, name="api_get_locale_settings"),
    path("api/settings/company/info/", views.api_get_company_info, name="api_get_company_info"),
    path("api/settings/2fa/save/", views.api_save_2fa_setting, name="api_save_2fa_setting"),
    path("api/settings/print-templates/save/", views.api_save_print_template_settings, name="api_save_print_template_settings"),
    path("api/customers/add/", views.api_add_customer, name="api_add_customer"),
    path("api/customers/<int:customer_id>/delete/", views.api_delete_customer, name="api_delete_customer"),
    path("api/notifications/<int:notification_id>/mark-read/", views.api_mark_notification_read, name="api_mark_notification_read"),
    path("api/notifications/<int:notification_id>/delete/", views.api_delete_notification, name="api_delete_notification"),
    path("api/notifications/preferences/save/", views.api_save_notification_preferences, name="api_save_notification_preferences"),
    path("api/notifications/search/", views.api_search_notifications, name="api_search_notifications"),
    path("api/storage/info/", views.api_get_storage_info, name="api_get_storage_info"),
    
    # Supplier CRUD
    path("suppliers/", views.supplier_list, name="supplier_list"),
    path("suppliers/create/", views.supplier_create, name="supplier_create"),
    path("suppliers/<int:pk>/edit/", views.supplier_edit, name="supplier_edit"),
    path("suppliers/<int:pk>/delete/", views.supplier_delete, name="supplier_delete"),
    
    # Tax CRUD
    path("taxes/", views.taxes, name="taxes"),
    path("taxes/save/", views.taxes_save, name="taxes_save"),
    path("taxes/create/", views.tax_create, name="tax_create"),
    path("taxes/<int:pk>/edit/", views.tax_edit, name="tax_edit"),
    path("taxes/<int:pk>/delete/", views.tax_delete, name="tax_delete"),
    
    # User Management
    path("users/", views.users_permissions, name="users_list"),
    path("users/create/", views.user_create, name="user_create"),
    path("users/<int:pk>/edit/", views.user_edit, name="user_edit"),
    path("users/<int:pk>/permissions/", views.user_permissions_update, name="user_permissions_update"),
    path("users/<int:pk>/delete/", views.user_delete, name="user_delete"),
    path("profile/", views.profile, name="profile"),
    path("profile/upload-avatar/", views.upload_avatar, name="upload_avatar"),
    path("profile/2fa/toggle/", views.toggle_two_factor, name="toggle_two_factor"),
    path("profile/subscription/upgrade/<str:plan_id>/", views.upgrade_subscription, name="upgrade_subscription"),
    path("profile/delete-account/", views.delete_account, name="delete_account"),
        path("profile/sessions/terminate/<int:session_id>/", views.terminate_session, name="terminate_session"),
        path("profile/sessions/terminate-all/", views.terminate_all_sessions, name="terminate_all_sessions"),
    
    # Search
    path("search/", views.search, name="search"),
    
    # Notification Actions
    path("notifications/create/", views.notification_create, name="notification_create"),
    path("notifications/mark-all-read/", views.notification_mark_all_read, name="notification_mark_all_read"),
    path("notifications/<int:pk>/delete/", views.notification_delete, name="notification_delete"),
    
    # Subscription Management
    path("subscription/", views.subscription, name="subscription"),
    
    # Category CRUD
    path("categories/", views.categories_list, name="categories_list"),
    path("categories/create/", views.category_create, name="category_create"),
    path("categories/<int:pk>/edit/", views.category_edit, name="category_edit"),
    path("categories/<int:pk>/delete/", views.category_delete, name="category_delete"),
    
    # Warehouse CRUD
    path("warehouses/create/", views.warehouse_create, name="warehouse_create"),
    path("warehouses/<int:pk>/edit/", views.warehouse_edit, name="warehouse_edit"),
    path("warehouses/<int:pk>/view/", views.warehouse_view, name="warehouse_view"),
    path("warehouses/<int:pk>/delete/", views.warehouse_delete, name="warehouse_delete"),
    
    # Authentication
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    
    # Dashboard Actions
    path("download-statement/", views.download_statement, name="download_statement"),
    path("create-bulk-purchase/", views.create_bulk_purchase, name="create_bulk_purchase"),
    
    # SSO Configuration Endpoints
    path("api/sso/config/", views.api_sso_config, name="api_sso_config"),
    path("api/sso/<str:provider_id>/enable/", views.api_sso_enable, name="api_sso_enable"),
    path("api/sso/<str:provider_id>/disable/", views.api_sso_disable, name="api_sso_disable"),
    path("api/sso/<str:provider_id>/configure/", views.api_sso_configure, name="api_sso_configure"),
    path("api/sso/map-role/", views.api_sso_map_role, name="api_sso_map_role"),
    path("api/sso/save/", views.api_sso_save, name="api_sso_save"),
    path("api/sso/load/", views.api_sso_load, name="api_sso_load"),
    path("api/get-current-user/", views.api_get_current_user, name="api_get_current_user"),
    path("api/get-security-status/", views.api_get_security_status, name="api_get_security_status"),
    
    # Additional pages for navigation
    path("invoices/", views.invoices_list, name="invoices_list"),
    path("help/", views.help_page, name="help_page"),
    path("privacy-policy/", views.privacy_policy, name="privacy_policy"),
    path("terms-of-service/", views.terms_of_service, name="terms_of_service"),
    path("support/", views.support_page, name="support_page"),
]
