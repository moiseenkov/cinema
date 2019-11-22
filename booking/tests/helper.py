from django.test import TestCase
from django.urls import reverse

from booking.models import CustomUser


class UserForTesting:
    def __init__(self, **kwargs):
        self.credentials = kwargs
        if kwargs.get('is_staff', None):
            self.user = CustomUser.objects.create_user(**kwargs)
        else:
            self.user = CustomUser.objects.create_superuser(**kwargs)
        self.user.save()


class LoggedInTestCase(TestCase):
    def _get_token(self, user):
        data = {
            'email': user.email,
            'password': user.password
        }
        response = self.client.put(path=reverse('token'), data=data)
        return response.data.get('access', None)

    def setUp(self) -> None:
        user_credentials = {
            'email': 'user@test.com',
            'password': 'user_password',
        }
        admin_credentials = {
            'email': 'admin@test.com',
            'password': 'admin_password',
            'is_staff': True
        }
        self.user = UserForTesting(**user_credentials).user
        self.admin = UserForTesting(**admin_credentials).user
        self.user_token = self._get_token(self.user)
        self.admin_token = self._get_token(self.admin)
        self.credentials = [
            user_credentials,
            admin_credentials,
        ]
        super(LoggedInTestCase, self).setUp()
