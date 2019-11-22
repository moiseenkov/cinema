from django.test import TestCase
from django.urls import reverse

from booking.models import CustomUser


class UserForTesting:
    def __init__(self, **kwargs):
        self.credentials = kwargs
        if kwargs.get('is_staff', None):
            self.user = CustomUser.objects.create_superuser(**kwargs)
        else:
            self.user = CustomUser.objects.create_user(**kwargs)
        self.user.save()


class LoggedInTestCase(TestCase):
    def _get_token(self, credentials):
        response = self.client.post(path=reverse('token'), data=credentials)
        return response.data.get('access', None)

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
        self.user = UserForTesting(**self.user_credentials).user
        self.admin = UserForTesting(**self.admin_credentials).user
        self.user_token = self._get_token(self.user_credentials)
        self.admin_token = self._get_token(self.admin_credentials)
        self.credentials = [
            self.user_credentials,
            self.admin_credentials,
        ]
        super(LoggedInTestCase, self).setUp()
