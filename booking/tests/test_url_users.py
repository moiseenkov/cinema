"""
Tests for endpoints:
 - /users/
 - /users/<int:pk>/
"""
from django.urls import reverse
from rest_framework import status

from booking.models import CustomUser
from booking.tests.helper import LoggedInTestCase


class UsersDetailURLPositiveTestCase(LoggedInTestCase):
    """
    Positive test case for user detail: /users/<int:pk>/
    """

    def test_url_users_detail_positive_get_user(self):
        """
        Positive test checks response for GET request to /users/<int:pk>/
        """
        url = reverse('user-detail', args=[self.user.pk])
        response = self.client.get(path=url, HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        expected_data = {
            'id': self.user.pk,
            'email': self.user.email,
            'password': self.user.password,
        }

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, expected_data)

    def test_url_users_detail_positive_get_admin_self(self):
        """
        Positive test checks response for admin's GET request to /users/<self>/
        """
        url = reverse('user-detail', args=[self.admin.pk])
        response = self.client.get(path=url, HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        expected_data = {
            'id': self.admin.pk,
            'email': self.admin.email,
            'is_staff': True,
            'is_active': True,
            'password': self.admin.password,
        }

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, expected_data)

    def test_url_users_detail_positive_get_admin_user(self):
        """
        Positive test checks response for admin's GET request to /users/<int:pk>/
        """
        url = reverse('user-detail', args=[self.user.pk])
        response = self.client.get(path=url, HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        expected_data = {
            'id': self.user.pk,
            'email': self.user.email,
            'is_staff': False,
            'is_active': True,
            'password': self.user.password,
        }

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, expected_data)

    def test_url_users_detail_positive_put_user(self):
        """
        Positive test checks response for user's PUT request to /users/<int:pk>/
        """
        url = reverse('user-detail', args=[self.user.pk])
        another_email = 'another_email@test.com'
        another_password = 'another password'
        input_data = {
            'email': another_email,
            'password': another_password,
        }
        response = self.client.put(path=url, data=input_data, content_type='application/json',
                                   HTTP_AUTHORIZATION=f'Bearer {self.user_token}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data.get('email', None))
        self.assertEqual(response.data['email'], another_email)

        user = CustomUser.objects.get(pk=self.user.pk)
        self.assertEqual(user.email, another_email)
        self.assertTrue(user.check_password(another_password))

    def test_url_users_detail_positive_put_admin_self(self):
        """
        Positive test checks response for admin's PUT request to /users/<self>/
        """
        url = reverse('user-detail', args=[self.admin.pk])
        another_email = 'another_email@test.com'
        another_password = 'another password'
        input_data = {
            'email': another_email,
            'is_staff': True,
            'is_active': True,
            'password': another_password
        }
        response = self.client.put(path=url, data=input_data, content_type='application/json',
                                   HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        admin = CustomUser.objects.get(pk=self.admin.pk)
        expected_data = {
            'id': self.admin.pk,
            'email': another_email,
            'is_staff': True,
            'is_active': True,
            'password': admin.password  # password should be hashed thus
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)
        self.assertTrue(admin.check_password(another_password))

    def test_url_users_detail_positive_put_admin_user(self):
        """
        Positive test checks response for admin's PUT request to /users/<int:pk>/
        """
        url = reverse('user-detail', args=[self.user.pk])
        another_email = 'another_email@test.com'
        another_password = 'another password'
        input_data = {
            'email': another_email,
            'is_staff': False,
            'is_active': True,
            'password': another_password
        }
        response = self.client.put(path=url, data=input_data, content_type='application/json',
                                   HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        user = CustomUser.objects.get(pk=self.user.pk)
        expected_data = {
            'id': self.user.pk,
            'email': another_email,
            'is_staff': False,
            'is_active': True,
            'password': user.password  # password should be hashed thus
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)
        self.assertTrue(user.check_password(another_password))

    def test_url_users_detail_positive_patch_user(self):
        """
        Positive test checks response for user's PATCH request to /users/<int:pk>/
        """
        url = reverse('user-detail', args=[self.user.pk])
        another_email = 'another_email@test.com'
        input_data = {
            'email': another_email,
        }
        response = self.client.patch(path=url, data=input_data, content_type='application/json',
                                     HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        expected_data = {
            'id': self.user.pk,
            'email': another_email,
            'password': self.user.password,
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

    def test_url_users_detail_positive_patch_admin_self(self):
        """
        Positive test checks response for admin's PATCH request to /users/<self>/
        """
        url = reverse('user-detail', args=[self.admin.pk])
        another_email = 'another_email@test.com'
        input_data = {
            'email': another_email,
        }
        response = self.client.patch(path=url, data=input_data, content_type='application/json',
                                     HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        expected_data = {
            'id': self.admin.pk,
            'email': another_email,
            'is_staff': True,
            'is_active': True,
            'password': self.admin.password
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

    def test_url_users_detail_positive_patch_admin_user(self):
        """
        Positive test checks response for admin's PATCH request to /users/<int:pk>/
        """
        url = reverse('user-detail', args=[self.user.pk])
        another_email = 'another_email@test.com'
        input_data = {
            'email': another_email,
        }
        response = self.client.patch(path=url, data=input_data, content_type='application/json',
                                     HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        expected_data = {
            'id': self.user.pk,
            'email': another_email,
            'is_staff': False,
            'is_active': True,
            'password': self.user.password
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

    def test_url_users_detail_positive_delete_user(self):
        """
        Positive test checks response for user's DELETE request to /users/<int:pk>/
        """
        url = reverse('user-detail', args=[self.user.pk])
        response = self.client.delete(path=url, HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(path=url, HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        self.assertContains(response=response,
                            text='User is inactive',
                            status_code=status.HTTP_401_UNAUTHORIZED)

    def test_url_users_detail_positive_delete_admin_self(self):
        """
        Positive test checks response for admin's DELETE request to /users/<self>/
        """
        url = reverse('user-detail', args=[self.admin.pk])
        response = self.client.delete(path=url, HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.delete(path=url, HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        self.assertContains(response=response,
                            text='User is inactive',
                            status_code=status.HTTP_401_UNAUTHORIZED)

    def test_url_users_detail_positive_delete_admin_user(self):
        """
        Positive test checks response for admin's DELETE request to /users/<int:pk>/
        """
        url = reverse('user-detail', args=[self.user.pk])
        response = self.client.delete(path=url, HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(path=url, HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_response = {
            'id': self.user.pk,
            'email': self.user.email,
            'is_active': False,
            'is_staff': False,
            'password': self.user.password,
        }
        self.assertDictEqual(response.data, expected_response)


class UsersDetailURLNegativeTestCase(LoggedInTestCase):
    """
    Negative test case for user detail: /users/<int:pk>/
    """

    def setUp(self) -> None:
        self.second_user = self._create_user(email='second@test.com', password='password')
        super(UsersDetailURLNegativeTestCase, self).setUp()

    def test_url_users_detail_negative_get_unauthorized(self):
        """
        Negative test checks that unauthorized user cannot get user detail via GET request
        """
        url = reverse('user-detail', args=[self.user.pk])
        response = self.client.get(path=url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_url_users_detail_negative_get_another_user(self):
        """
        Negative test checks that authorized user cannot get other user's detail via GET request
        """
        url = reverse('user-detail', args=[self.second_user.pk])
        response = self.client.get(path=url, HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_url_users_detail_negative_put_wrong_email_user(self):
        """
        Negative test checks that user cannot reuse someone's else email
        """
        url = reverse('user-detail', args=[self.user.pk])
        input_data = {
            'email': self.second_user.email,
            'password': 'new password'
        }
        response = self.client.put(path=url, data=input_data, content_type='application/json',
                                   HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_url_users_detail_negative_put_wrong_email_admin(self):
        """
        Negative test checks that admin cannot reuse someone's else email
        """
        url = reverse('user-detail', args=[self.user.pk])
        input_data = {
            'email': self.second_user.email,
            'password': 'new password'
        }
        response = self.client.put(path=url, data=input_data, content_type='application/json',
                                   HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_url_users_detail_negative_put_not_all_fields(self):
        """
        Negative test checks that email and passwords required
        """
        url = reverse('user-detail', args=[self.user.pk])
        data = {
            'email': 'changed_email@test.com'
        }
        response = self.client.put(path=url, data=data, content_type='application/json',
                                   HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UsersListURLPositiveTestCase(LoggedInTestCase):
    """
    Positive test case for user list: /users/
    """

    def setUp(self) -> None:
        self.url_list = reverse('user-list')
        self.another_user_credentials = {
            'email': 'another_email@test.com',
            'password': 'password',
            'is_staff': False,
            'is_active': True,
        }
        super(UsersListURLPositiveTestCase, self).setUp()

    def test_url_users_list_positive_get_user(self):
        """
        Positive test checks response for user's GET request to /users/
        """
        response = self.client.get(path=self.url_list,
                                   HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        expected_result = {
            'id': self.user.pk,
            'email': self.user.email,
            'password': self.user.password,
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data.get('results', None))
        data = response.data['results']
        self.assertEqual(len(data), 1)
        self.assertDictEqual(dict(data[0]), expected_result)

    def test_url_users_list_positive_get_admin(self):
        """
        Positive test checks response for admin's GET request to /users/
        """
        response = self.client.get(path=self.url_list,
                                   HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        expected_result = [
            {
                'id': self.user.pk,
                'email': self.user.email,
                'is_active': True,
                'is_staff': False,
                'password': self.user.password,
            },
            {
                'id': self.admin.pk,
                'email': self.admin.email,
                'is_active': True,
                'is_staff': True,
                'password': self.admin.password,
            },
        ]
        expected_result.sort(key=lambda user: user['id'], reverse=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data.get('results', None))
        data = response.data['results']
        self.assertEqual(len(data), 2)
        for given_user, expected_user in zip(data, expected_result):
            with self.subTest(given_user=given_user, expected_user=expected_user):
                self.assertDictEqual(given_user, expected_user)

    def test_url_users_list_positive_post_unauthorized(self):
        """
        Positive test checks response for anonymous user POST (sign up) request to /users/
        """
        email = self.another_user_credentials['email']
        password = self.another_user_credentials['password']
        response = self.client.post(path=self.url_list, data=self.another_user_credentials)

        user = CustomUser.objects.filter(email=email).first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, email)
        self.assertNotEqual(user.password, password)  # password should be hashed
        self.assertTrue(user.check_password(password))
        expected_response = {
            'id': user.pk,
            'email': user.email,
            'password': user.password,
        }
        self.assertDictEqual(response.data, expected_response)

    def test_url_users_list_positive_post_admin(self):
        """
        Positive test checks response for admin's POST (sign up) request to /users/
        """
        email = self.another_user_credentials['email']
        password = self.another_user_credentials['password']
        response = self.client.post(path=self.url_list, data=self.another_user_credentials,
                                    HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')

        new_user = CustomUser.objects.filter(email=email).first()
        self.assertIsNotNone(new_user)
        self.assertEqual(new_user.email, email)
        self.assertNotEqual(new_user.password, password)  # password should be hashed
        self.assertTrue(new_user.check_password(password))

        expected_response = {
            'id': new_user.pk,
            'email': new_user.email,
            'password': new_user.password,
            'is_staff': False,
            'is_active': True,
        }
        self.assertDictEqual(response.data, expected_response)

    def test_url_users_list_positive_post_create_admin_by_admin(self):
        """
        Positive test checks that admin can create admin
        """
        credentials = {
            'email': 'admin_by_admin@test.com',
            'password': 'password',
            'is_staff': True,
            'is_active': True,
        }
        response = self.client.post(path=self.url_list, data=credentials,
                                    HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_admin = CustomUser.objects.filter(pk=response.data['id']).first()
        self.assertIsNotNone(new_admin)
        expected_data = {
            'id': new_admin.pk,
            'email': credentials['email'],
            'password': new_admin.password,
            'is_staff': credentials['is_staff'],
            'is_active': True,
        }
        self.assertDictEqual(response.data, expected_data)


class UsersListURLNegativeTestCase(LoggedInTestCase):
    """
    Negative test for /users/
    """

    def setUp(self) -> None:
        self.url_list = reverse('user-list')
        super(UsersListURLNegativeTestCase, self).setUp()

    def test_url_users_list_negative_get_unauthorized(self):
        """
        Negative test checks that unauthorised uer cannot see any user information
        """
        response = self.client.get(path=self.url_list)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data.get('results', None))
        self.assertEqual(response.data['results'], [])

    def test_url_users_list_negative_post_invalid_email(self):
        """
        Negative test checks that anonymous user cannot signup with invalid credentials
        """
        credentials = {
            'email': 'invalid',
            'password': 'password',
        }
        response = self.client.post(path=self.url_list, data=credentials)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_url_users_list_negative_post_missed_password(self):
        """
        Negative test checks password required during signing up
        """
        credentials = {
            'email': 'test_user@test.com',
        }
        response = self.client.post(path=self.url_list, data=credentials)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_url_users_list_negative_post_existing_email(self):
        """
        Negative test checks that user cannot sign up with someone's else email
        """
        credentials = {
            'email': self.user.email,
            'password': 'password',
        }
        response = self.client.post(path=self.url_list, data=credentials)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_url_users_list_negative_post_create_admin_user(self):
        """
        Negative test checks that user cannot create admin
        """
        credentials = {
            'email': 'user_admin1@test.com',
            'password': 'password',
            'is_staff': True,
        }
        response = self.client.post(path=self.url_list,
                                    data=credentials,
                                    HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = CustomUser.objects.get(pk=response.data['id'])
        self.assertEqual(user.is_staff, False)
