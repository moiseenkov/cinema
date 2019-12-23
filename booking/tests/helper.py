"""
Test helper module contains classes reusable in tests
"""
from django.test import TestCase
from django.urls import reverse

from booking.models import CustomUser


class LoggedInTestCase(TestCase):
    """
    Base test case that provides user and admin instances for further testing
    """
    def _get_token(self, credentials):
        response = self.client.post(path=reverse('token'), data=credentials)
        return response.data.get('access', None)

    @staticmethod
    def _create_user(**kwargs):
        if kwargs.get('is_staff', None):
            user = CustomUser.objects.create_superuser(**kwargs)
        else:
            user = CustomUser.objects.create_user(**kwargs)
        user.save()
        return user

    def setUp(self) -> None:
        self.user_credentials = {
            'email': 'user@test.com',
            'password': 'user_password',
        }
        self.admin_credentials = {
            'email': 'admin@test.com',
            'password': 'admin_password',
            'is_staff': True
        }
        self.user = self._create_user(**self.user_credentials)
        self.admin = self._create_user(**self.admin_credentials)
        self.user_token = self._get_token(self.user_credentials)
        self.admin_token = self._get_token(self.admin_credentials)
        self.credentials = [
            self.user_credentials,
            self.admin_credentials,
        ]
        super(LoggedInTestCase, self).setUp()
