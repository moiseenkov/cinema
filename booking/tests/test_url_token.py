from rest_framework import status

from booking.tests.helper import LoggedInUserTestCase, LoggedInAdminTestCase


class TestTokenMixin:
    """
    Mixin class contains tests
    """

    def test_login_response_code(self):
        self.assertEqual(self.response.status_code, status.HTTP_200_OK)

    def test_login_response_data(self):
        data = self.response.data
        self.assertIsNotNone(data)
        self.assertEqual(type(data), dict)
        self.assertSetEqual(set(data.keys()), {'access', 'refresh'})

    def test_login_without_credentials(self):
        response = self.client.post(self.url_login, {})
        self.assertContains(response=response, status_code=status.HTTP_400_BAD_REQUEST, text='This field is required',
                            count=2)
        self.assertContains(response=response, status_code=status.HTTP_400_BAD_REQUEST, text='email')
        self.assertContains(response=response, status_code=status.HTTP_400_BAD_REQUEST, text='password')

    def test_login_incorrect_credentials(self):
        not_exist = {
            'email': 'wrong email',
            'password': 'wrong password'
        }
        response = self.client.post(self.url_login, not_exist)
        self.assertContains(response=response, status_code=status.HTTP_401_UNAUTHORIZED,
                            text='No active account found with the given credentials')

    def test_login_wrong_methods(self):
        response = self.client.get(self.url_login, self.credentials)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        response = self.client.put(self.url_login, self.credentials)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        response = self.client.patch(self.url_login, self.credentials)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        response = self.client.delete(self.url_login, self.credentials)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class TestTokenUser(TestTokenMixin, LoggedInUserTestCase):
    def setUp(self) -> None:
        super(TestTokenUser, self).setUp()


class TestTokenAdmin(TestTokenMixin, LoggedInAdminTestCase):
    def setUp(self) -> None:
        super(TestTokenAdmin, self).setUp()
