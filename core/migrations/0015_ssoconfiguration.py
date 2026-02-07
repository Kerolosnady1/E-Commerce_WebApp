# Generated migration for SSOConfiguration model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0014_module_rolepermission'),
    ]

    operations = [
        migrations.CreateModel(
            name='SSOConfiguration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('provider', models.CharField(choices=[('google', 'Google OAuth2'), ('azure', 'Microsoft Azure AD'), ('saml2', 'SAML 2.0'), ('ldap', 'LDAP/Active Directory')], max_length=20, unique=True)),
                ('is_enabled', models.BooleanField(default=False)),
                ('google_client_id', models.CharField(blank=True, max_length=255)),
                ('google_client_secret', models.CharField(blank=True, max_length=255)),
                ('azure_tenant_id', models.CharField(blank=True, max_length=255)),
                ('azure_client_id', models.CharField(blank=True, max_length=255)),
                ('azure_client_secret', models.CharField(blank=True, max_length=255)),
                ('saml_entity_id', models.CharField(blank=True, max_length=500)),
                ('saml_sso_url', models.URLField(blank=True)),
                ('saml_certificate', models.TextField(blank=True)),
                ('ldap_server_uri', models.CharField(blank=True, max_length=500)),
                ('ldap_bind_dn', models.CharField(blank=True, max_length=500)),
                ('ldap_bind_password', models.CharField(blank=True, max_length=255)),
                ('ldap_user_search_base', models.CharField(blank=True, max_length=500)),
                ('ldap_group_search_base', models.CharField(blank=True, max_length=500)),
                ('role_mapping', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'إعدادات SSO',
                'verbose_name_plural': 'إعدادات SSO',
                'ordering': ['provider'],
            },
        ),
    ]
