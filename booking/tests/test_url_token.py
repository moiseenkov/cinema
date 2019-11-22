from django.urls import reverse
from rest_framework import status

from booking.tests.helper import LoggedInTestCase


class LoginURLPositiveTestCase(LoggedInTestCase):
    def setUp(self) -> None:
        self.url_login = reverse('token')
        super(LoginURLPositiveTestCase, self).setUp()

    def test_url_login_positive_POST(self):
        for cred in self.credentials:
            with self.subTest(cred=cred):
                response = self.client.post(path=self.url_login, data=cred)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertIsNotNone(response.data.get('access', None))
                self.assertGreater(response.data['access'], '')
                self.assertIsNotNone(response.data.get('refresh', None))
                self.assertGreater(response.data['refresh'], '')

    def test_url_login_positive_GET(self):
        for cred in self.credentials:
            with self.subTest(cred=cred):
                response = self.client.get(path=self.url_login, data=cred)
                self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_url_login_positive_PUT(self):
        for cred in self.credentials:
            with self.subTest(cred=cred):
                response = self.client.put(path=self.url_login, data=cred)
                self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_url_login_positive_PATCH(self):
        for cred in self.credentials:
            with self.subTest(cred=cred):
                response = self.client.patch(path=self.url_login, data=cred)
                self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_url_login_positive_DELETE(self):
        for cred in self.credentials:
            with self.subTest(cred=cred):
                response = self.client.delete(path=self.url_login, data=cred)
                self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
