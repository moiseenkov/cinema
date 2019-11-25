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


class LoginURLNegativeTestCase(LoggedInTestCase):
    def setUp(self) -> None:
        self.url_login = reverse('token')
        super(LoginURLNegativeTestCase, self).setUp()

    def test_url_login_negative_POST_no_password(self):
        credentials = {
            'email': self.credentials[0]['email']
        }
        response = self.client.post(path=self.url_login, data=credentials)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_url_login_negative_POST_no_email(self):
        credentials = {
            'password': self.credentials[0]['password']
        }
        response = self.client.post(path=self.url_login, data=credentials)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_url_login_negative_POST_wrong_email(self):
        credentials = self.credentials[0].copy()
        credentials['email'] = 'another@test.com'

        response = self.client.post(path=self.url_login, data=credentials)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_url_login_negative_POST_wrong_password(self):
        credentials = self.credentials[0].copy()
        credentials['password'] = 'wrong password'

        response = self.client.post(path=self.url_login, data=credentials)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_url_login_negative_POST_incorrect_email(self):
        credentials = self.credentials[0].copy()
        credentials['email'] = r'incorrect email'

        response = self.client.post(path=self.url_login, data=credentials)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)