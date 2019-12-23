"""
Tests for endpoint:
 - /token/
"""
from django.urls import reverse
from rest_framework import status

from booking.tests.helper import LoggedInTestCase


class LoginURLPositiveTestCase(LoggedInTestCase):
    """
    Positive test case for getting JWT token: /token/
    """
    def setUp(self) -> None:
        self.url_login = reverse('token')
        super(LoginURLPositiveTestCase, self).setUp()

    def test_url_login_positive_post(self):
        """
        Positive test checks response for POST request to /token/
        """
        for cred in self.credentials:
            with self.subTest(cred=cred):
                response = self.client.post(path=self.url_login, data=cred)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertIsNotNone(response.data.get('access', None))
                self.assertGreater(response.data['access'], '')
                self.assertIsNotNone(response.data.get('refresh', None))
                self.assertGreater(response.data['refresh'], '')


class LoginURLNegativeTestCase(LoggedInTestCase):
    """
    Negative test case for getting JWT token: /token/
    """
    def setUp(self) -> None:
        self.url_login = reverse('token')
        super(LoginURLNegativeTestCase, self).setUp()

    def test_url_login_negative_get(self):
        """
        Negative test checks response for GET request to /token/
        """
        for cred in self.credentials:
            with self.subTest(cred=cred):
                response = self.client.get(path=self.url_login, data=cred)
                self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_url_login_negative_put(self):
        """
        Negative test checks response for PUT request to /token/
        """
        for cred in self.credentials:
            with self.subTest(cred=cred):
                response = self.client.put(path=self.url_login, data=cred)
                self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_url_login_negative_patch(self):
        """
        Negative test checks response for PATCH request to /token/
        """
        for cred in self.credentials:
            with self.subTest(cred=cred):
                response = self.client.patch(path=self.url_login, data=cred)
                self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_url_login_negative_delete(self):
        """
        Negative test checks response for DELETE request to /token/
        """
        for cred in self.credentials:
            with self.subTest(cred=cred):
                response = self.client.delete(path=self.url_login, data=cred)
                self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_url_login_negative_post_no_password(self):
        """
        Negative test checks that password is required
        """
        credentials = {
            'email': self.credentials[0]['email']
        }
        response = self.client.post(path=self.url_login, data=credentials)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_url_login_negative_post_no_email(self):
        """
        Negative test checks that email is required
        """
        credentials = {
            'password': self.credentials[0]['password']
        }
        response = self.client.post(path=self.url_login, data=credentials)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_url_login_negative_post_wrong_email(self):
        """
        Negative test checks wrong email
        """
        credentials = self.credentials[0].copy()
        credentials['email'] = 'another@test.com'

        response = self.client.post(path=self.url_login, data=credentials)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_url_login_negative_post_wrong_password(self):
        """
        Negative test checks wrong password
        """
        credentials = self.credentials[0].copy()
        credentials['password'] = 'wrong password'

        response = self.client.post(path=self.url_login, data=credentials)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_url_login_negative_post_incorrect_email(self):
        """
        Negative test checks incorrect email
        """
        credentials = self.credentials[0].copy()
        credentials['email'] = r'incorrect email'

        response = self.client.post(path=self.url_login, data=credentials)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
