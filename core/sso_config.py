"""
SSO (Single Sign-On) Configuration Module
Handles OAuth2, SAML, and LDAP configurations for different roles
"""

from django.conf import settings
from django.contrib.auth.models import Group


class SSOProvider:
    """Base class for SSO providers"""
    
    def __init__(self, name, provider_id):
        self.name = name
        self.provider_id = provider_id
        self.is_enabled = False
        self.config = {}
    
    def enable(self):
        self.is_enabled = True
    
    def disable(self):
        self.is_enabled = False
    
    def set_config(self, **kwargs):
        self.config.update(kwargs)
    
    def get_config(self):
        return self.config


class GoogleSSO(SSOProvider):
    """Google OAuth2 SSO Provider"""
    
    def __init__(self):
        super().__init__("Google", "google")
        self.default_config = {
            'client_id': settings.GOOGLE_CLIENT_ID if hasattr(settings, 'GOOGLE_CLIENT_ID') else '',
            'client_secret': settings.GOOGLE_CLIENT_SECRET if hasattr(settings, 'GOOGLE_CLIENT_SECRET') else '',
            'redirect_uri': '/api/auth/google/callback/',
            'scopes': ['openid', 'email', 'profile'],
        }
        self.config = self.default_config.copy()


class MicrosoftAzureSSO(SSOProvider):
    """Microsoft Azure AD SSO Provider"""
    
    def __init__(self):
        super().__init__("Microsoft Azure", "azure")
        self.default_config = {
            'tenant_id': settings.AZURE_TENANT_ID if hasattr(settings, 'AZURE_TENANT_ID') else '',
            'client_id': settings.AZURE_CLIENT_ID if hasattr(settings, 'AZURE_CLIENT_ID') else '',
            'client_secret': settings.AZURE_CLIENT_SECRET if hasattr(settings, 'AZURE_CLIENT_SECRET') else '',
            'redirect_uri': '/api/auth/azure/callback/',
            'authority': 'https://login.microsoftonline.com/{tenant_id}',
        }
        self.config = self.default_config.copy()


class SAML2SSO(SSOProvider):
    """SAML 2.0 SSO Provider"""
    
    def __init__(self):
        super().__init__("SAML 2.0", "saml2")
        self.default_config = {
            'sp_entity_id': 'https://yourdomain.com/saml/metadata/',
            'idp_entity_id': '',
            'idp_sso_url': '',
            'idp_certificate': '',
            'name_id_format': 'urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress',
        }
        self.config = self.default_config.copy()


class LDAPSO(SSOProvider):
    """LDAP/Active Directory SSO Provider"""
    
    def __init__(self):
        super().__init__("LDAP/Active Directory", "ldap")
        self.default_config = {
            'server_uri': settings.LDAP_SERVER if hasattr(settings, 'LDAP_SERVER') else 'ldap://localhost',
            'bind_dn': settings.LDAP_BIND_DN if hasattr(settings, 'LDAP_BIND_DN') else '',
            'bind_password': settings.LDAP_BIND_PASSWORD if hasattr(settings, 'LDAP_BIND_PASSWORD') else '',
            'user_search_base': settings.LDAP_USER_SEARCH_BASE if hasattr(settings, 'LDAP_USER_SEARCH_BASE') else 'ou=users,dc=example,dc=com',
            'user_search_filter': '(uid=%(user)s)',
            'group_search_base': settings.LDAP_GROUP_SEARCH_BASE if hasattr(settings, 'LDAP_GROUP_SEARCH_BASE') else 'ou=groups,dc=example,dc=com',
        }
        self.config = self.default_config.copy()


class SSOManager:
    """Manages all SSO providers and role mappings"""
    
    def __init__(self):
        self.providers = {
            'google': GoogleSSO(),
            'azure': MicrosoftAzureSSO(),
            'saml2': SAML2SSO(),
            'ldap': LDAPSO(),
        }
        
        # Default role mappings
        self.role_mappings = {
            'مدير النظام': {
                'google_group': 'Admins',
                'azure_group': 'Admin Group',
                'saml_group': 'admin',
                'ldap_group': 'admins',
            },
            'قسم المبيعات': {
                'google_group': 'Sales Team',
                'azure_group': 'Sales Group',
                'saml_group': 'sales',
                'ldap_group': 'sales',
            },
            'المحاسب': {
                'google_group': 'Accounting',
                'azure_group': 'Finance Group',
                'saml_group': 'accounting',
                'ldap_group': 'accounting',
            },
            'مدير المستودع': {
                'google_group': 'Warehouse',
                'azure_group': 'Warehouse Group',
                'saml_group': 'warehouse',
                'ldap_group': 'warehouse',
            },
        }
    
    def get_provider(self, provider_id):
        """Get SSO provider by ID"""
        return self.providers.get(provider_id)
    
    def get_all_providers(self):
        """Get all SSO providers"""
        return self.providers
    
    def enable_provider(self, provider_id):
        """Enable an SSO provider"""
        provider = self.get_provider(provider_id)
        if provider:
            provider.enable()
            return True
        return False
    
    def disable_provider(self, provider_id):
        """Disable an SSO provider"""
        provider = self.get_provider(provider_id)
        if provider:
            provider.disable()
            return True
        return False
    
    def configure_provider(self, provider_id, **config):
        """Configure SSO provider settings"""
        provider = self.get_provider(provider_id)
        if provider:
            provider.set_config(**config)
            return True
        return False
    
    def map_sso_to_role(self, provider_id, sso_group, django_role):
        """Map SSO group to Django role"""
        if django_role in self.role_mappings:
            self.role_mappings[django_role][f'{provider_id}_group'] = sso_group
            return True
        return False
    
    def get_role_mapping(self):
        """Get all role mappings"""
        return self.role_mappings
    
    def assign_role_from_sso(self, user, provider_id, sso_groups):
        """Assign Django role to user based on SSO groups"""
        try:
            for role_name, mapping in self.role_mappings.items():
                provider_key = f'{provider_id}_group'
                if provider_key in mapping:
                    required_group = mapping[provider_key]
                    if required_group in sso_groups:
                        group = Group.objects.get(name=role_name)
                        user.groups.add(group)
                        return role_name
            return None
        except Exception as e:
            print(f"Error assigning role from SSO: {e}")
            return None


# Initialize global SSO manager
sso_manager = SSOManager()
