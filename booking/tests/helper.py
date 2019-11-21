from django.test import TestCase
from django.urls import reverse

from booking.models import CustomUser, Hall


def get_halls_dict():
    """
    Returns dictionary that contains information about all halls from database with following fields:
    {
        'id': ...,
        'rows_count': ...,
        'rows_size': ...,
        'seats_count': ...,  # This value calculates as a rows_count * rows_size
    }
    :return: Dict that contains information about all halls from database
    """
    return [{
        'id': hall.pk,
        'name': hall.name,
        'rows_count': hall.rows_count,
        'rows_size': hall.rows_size,
        'seats_count': hall.rows_count * hall.rows_size,
    } for hall in Hall.objects.all()]


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
        self.response = self.client.post(self.url_login, self.credentials)
        self.token = self.response.data.get('access', None)


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
