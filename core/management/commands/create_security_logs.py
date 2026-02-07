from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random
from core.models import SecurityLog


class Command(BaseCommand):
    help = 'إنشاء بيانات تجريبية لسجلات الأمان'

    def handle(self, *args, **kwargs):
        # Get or create sample users
        users = list(User.objects.all()[:5])
        if not users:
            self.stdout.write(self.style.WARNING('لا يوجد مستخدمين. الرجاء إنشاء مستخدمين أولاً.'))
            return
        
        # Sample data
        actions = [
            ('login_success', 'دخول ناجح للنظام', 'success'),
            ('login_failed', 'محاولة دخول بكلمة مرور خاطئة', 'failed'),
            ('logout', 'تسجيل خروج آمن', 'success'),
            ('permission_change', 'تعديل صلاحيات المستخدم', 'success'),
            ('settings_change', 'تفعيل Google SSO وربط الأدوار', 'success'),
            ('role_change', 'تغيير دور المستخدم إلى مدير النظام', 'success'),
            ('user_created', 'إنشاء مستخدم جديد في النظام', 'success'),
            ('data_export', 'تصدير بيانات العملاء إلى CSV', 'warning'),
            ('password_change', 'تغيير كلمة المرور بنجاح', 'success'),
            ('2fa_enabled', 'تفعيل المصادقة الثنائية (2FA)', 'success'),
            ('suspicious_activity', 'وصول من موقع جغرافي غير معروف', 'warning'),
            ('multiple_failed', '5 محاولات دخول فاشلة متتالية', 'failed'),
        ]
        
        devices = ['Desktop', 'Mobile', 'Tablet']
        browsers = ['Chrome', 'Firefox', 'Safari', 'Edge']
        ips = [
            '192.168.1.45', '192.168.1.105', '192.168.1.78',
            '203.45.123.67', '41.233.12.89', '10.0.0.15'
        ]
        
        # Create 50 sample security logs
        SecurityLog.objects.all().delete()  # Clear existing logs
        
        for i in range(50):
            user = random.choice(users)
            action_type, description, status = random.choice(actions)
            device = random.choice(devices)
            browser = random.choice(browsers)
            ip = random.choice(ips)
            
            # Create log with random timestamp in last 7 days
            days_ago = random.randint(0, 7)
            hours_ago = random.randint(0, 23)
            minutes_ago = random.randint(0, 59)
            
            timestamp = timezone.now() - timedelta(
                days=days_ago,
                hours=hours_ago,
                minutes=minutes_ago
            )
            
            log = SecurityLog.objects.create(
                user=user,
                username=user.username,
                action_type=action_type,
                description=description,
                ip_address=ip,
                user_agent=f'Mozilla/5.0 ({device}) {browser}',
                device_type=device,
                browser=browser,
                status=status,
            )
            
            # Set custom timestamp
            log.timestamp = timestamp
            log.save()
        
        self.stdout.write(self.style.SUCCESS('تم إنشاء 50 سجل أمان تجريبي بنجاح!'))
