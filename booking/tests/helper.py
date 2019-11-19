from django.test import TestCase, Client
from django.urls import reverse

from booking.models import CustomUser


class LoginTestCase(TestCase):
    """
    Base class for TestCases that require user authentication.
    Attribute 'self.credentials' need to be specified in every derived class:
    self.credentials = {
            'email': 'user@test.com',
            'password': 'user'
        }
    """
    def setUp(self) -> None:
        self.url_login = reverse('token')
        self.client = Client()
        self.response = self.client.post(self.url_login, self.credentials)


class LoggedInUserTestCase(LoginTestCase):
    """
    Test case provides ready logged in user (CustomUser instance)
    """
    def setUp(self) -> None:
        self.credentials = {
            'email': 'user@test.com',
            'password': 'user'
        }
        user = CustomUser.objects.create_user(**self.credentials)
        user.save()
        self.user = user
        super(LoggedInUserTestCase, self).setUp()


class LoggedInAdminTestCase(LoginTestCase):
    """
        Test case provides ready logged in admin (CustomUser instance)
        """
    def setUp(self) -> None:
        self.credentials = {
            'email': 'admin@test.com',
            'password': 'admin'
        }
        admin = CustomUser.objects.create_superuser(**self.credentials)
        admin.save()
        self.admin = admin
        super(LoggedInAdminTestCase, self).setUp()
