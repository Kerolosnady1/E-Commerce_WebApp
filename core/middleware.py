from django.utils import timezone
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def parse_user_agent(user_agent_string):
    """Parse user agent string to extract device, browser, and OS info"""
    ua = user_agent_string.lower()
    
    # Detect device type
    if 'mobile' in ua or 'android' in ua:
        device_type = 'Mobile'
    elif 'tablet' in ua or 'ipad' in ua:
        device_type = 'Tablet'
    else:
        device_type = 'Desktop'
    
    # Detect browser
    if 'edg' in ua:
        browser = 'Edge'
    elif 'chrome' in ua:
        browser = 'Chrome'
    elif 'safari' in ua and 'chrome' not in ua:
        browser = 'Safari'
    elif 'firefox' in ua:
        browser = 'Firefox'
    elif 'opera' in ua or 'opr' in ua:
        browser = 'Opera'
    else:
        browser = 'Unknown'
    
    # Detect OS
    if 'windows' in ua:
        if 'nt 10.0' in ua:
            os = 'Windows 10/11'
        elif 'nt 6.3' in ua:
            os = 'Windows 8.1'
        elif 'nt 6.2' in ua:
            os = 'Windows 8'
        elif 'nt 6.1' in ua:
            os = 'Windows 7'
        else:
            os = 'Windows'
    elif 'mac os x' in ua:
        os = 'macOS'
    elif 'iphone' in ua:
        os = 'iOS'
    elif 'ipad' in ua:
        os = 'iPadOS'
    elif 'android' in ua:
        os = 'Android'
    elif 'linux' in ua:
        os = 'Linux'
    else:
        os = 'Unknown'
    
    return device_type, browser, os


class SessionTrackingMiddleware:
    """Middleware to track user sessions"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and hasattr(request, 'session'):
            from .models import UserSession
            
            session_key = request.session.session_key
            if session_key:
                # Get or create session record
                user_agent = request.META.get('HTTP_USER_AGENT', '')
                device_type, browser, os = parse_user_agent(user_agent)
                ip_address = get_client_ip(request)
                
                session, created = UserSession.objects.get_or_create(
                    session_key=session_key,
                    defaults={
                        'user': request.user,
                        'ip_address': ip_address,
                        'user_agent': user_agent,
                        'device_type': device_type,
                        'browser': browser,
                        'os': os,
                        'is_current': True
                    }
                )
                
                if not created:
                    # Update last activity
                    session.last_activity = timezone.now()
                    session.save(update_fields=['last_activity'])

        response = self.get_response(request)
        return response


@receiver(user_logged_in)
def track_user_login(sender, request, user, **kwargs):
    """Track user session on login"""
    from .models import UserSession, SecurityLog
    
    if hasattr(request, 'session'):
        session_key = request.session.session_key
        if session_key:
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            device_type, browser, os = parse_user_agent(user_agent)
            ip_address = get_client_ip(request)
            
            # Mark all other sessions as not current
            UserSession.objects.filter(user=user).update(is_current=False)
            
            # Create or update current session
            UserSession.objects.update_or_create(
                session_key=session_key,
                defaults={
                    'user': user,
                    'ip_address': ip_address,
                    'user_agent': user_agent,
                    'device_type': device_type,
                    'browser': browser,
                    'os': os,
                    'is_current': True
                }
            )
            
            # Create security log for successful login
            SecurityLog.objects.create(
                user=user,
                username=user.username,
                action_type='login_success',
                description=f'دخول ناجح للنظام من {device_type} - {browser}',
                ip_address=ip_address,
                user_agent=user_agent,
                device_type=device_type,
                browser=browser,
                status='success'
            )
