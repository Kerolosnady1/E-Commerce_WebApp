"""
Test suite for Notification Center functionality
"""

import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from core.models import Notification


class NotificationCenterTestCase(TestCase):
    """Test notification center views and API endpoints"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = Client()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test notifications
        self.notif1 = Notification.objects.create(
            title='Test Notification 1',
            message='This is a test notification',
            level='info',
            is_read=False
        )
        
        self.notif2 = Notification.objects.create(
            title='Test Notification 2',
            message='This is another test notification',
            level='warning',
            is_read=True
        )
    
    def test_notifications_page_loads(self):
        """Test that notifications page loads successfully"""
        response = self.client.get('/notifications/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, '10-Notifications_Center_System_Code.html')
    
    def test_notifications_context(self):
        """Test that notifications are passed in context"""
        response = self.client.get('/notifications/')
        self.assertIn('notifications', response.context)
        self.assertIn('unread_count', response.context)
        self.assertIn('total_count', response.context)
    
    def test_unread_count(self):
        """Test that unread count is correct"""
        response = self.client.get('/notifications/')
        self.assertEqual(response.context['unread_count'], 1)
    
    def test_total_count(self):
        """Test that total count is correct"""
        response = self.client.get('/notifications/')
        self.assertEqual(response.context['total_count'], 2)
    
    def test_api_mark_notification_read(self):
        """Test API endpoint to mark notification as read"""
        response = self.client.post(f'/api/notifications/{self.notif1.id}/mark-read/')
        
        self.assertEqual(response.status_code, 200)
        
        # Verify notification is marked as read
        self.notif1.refresh_from_db()
        self.assertTrue(self.notif1.is_read)
    
    def test_api_delete_notification(self):
        """Test API endpoint to delete notification"""
        notif_id = self.notif1.id
        response = self.client.post(f'/api/notifications/{notif_id}/delete/')
        
        self.assertEqual(response.status_code, 200)
        
        # Verify notification is deleted
        self.assertFalse(Notification.objects.filter(id=notif_id).exists())
    
    def test_api_save_notification_preferences(self):
        """Test API endpoint to save notification preferences"""
        data = {
            'in_app': True,
            'email': True,
            'sms': False
        }
        
        response = self.client.post(
            '/api/notifications/preferences/save/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
    
    def test_notification_levels(self):
        """Test different notification levels"""
        levels = ['info', 'warning', 'error', 'success']
        
        for level in levels:
            notif = Notification.objects.create(
                title=f'Test {level}',
                message=f'This is a {level} notification',
                level=level,
                is_read=False
            )
            self.assertEqual(notif.level, level)


class NotificationUITestCase(TestCase):
    """Test notification center UI components"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create test notifications
        for i in range(5):
            Notification.objects.create(
                title=f'Notification {i+1}',
                message=f'Message {i+1}',
                level='info' if i % 2 == 0 else 'warning',
                is_read=False if i < 3 else True
            )
    
    def test_recent_tab_data(self):
        """Test recent notifications tab data"""
        response = self.client.get('/notifications/')
        notifications = response.context['notifications']
        
        self.assertEqual(len(notifications), 5)
        self.assertTrue(all(notif.title.startswith('Notification') for notif in notifications))
    
    def test_archive_tab_data(self):
        """Test archive notifications tab data"""
        response = self.client.get('/notifications/')
        read_notifications = response.context.get('read_notifications', [])
        
        # Count read notifications
        read_count = Notification.objects.filter(is_read=True).count()
        self.assertEqual(read_count, 2)
    
    def test_statistics_cards(self):
        """Test statistics cards data"""
        response = self.client.get('/notifications/')
        
        self.assertEqual(response.context['total_count'], 5)
        self.assertEqual(response.context['unread_count'], 3)
        self.assertIn('error_count', response.context)
        self.assertIn('warning_count', response.context)
        self.assertIn('success_count', response.context)


if __name__ == '__main__':
    import unittest
    unittest.main()
