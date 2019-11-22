from django.urls import reverse
from rest_framework import status

from booking.models import CustomUser
from booking.tests.helper import LoggedInTestCase


class UsersDetailURLPositiveTestCase(LoggedInTestCase):
    def test_url_users_detail_positive_GET_user(self):
        url = reverse('user-detail', args=[self.user.pk])
        response = self.client.get(path=url, HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        expected_data = {
            'id': self.user.pk,
            'email': self.user.email
        }

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, expected_data)

    def test_url_users_detail_positive_GET_admin_self(self):
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

    def test_url_users_detail_positive_GET_admin_user(self):
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

    def test_url_users_detail_positive_PUT_user(self):
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

    def test_url_users_detail_positive_PUT_admin_self(self):
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

    def test_url_users_detail_positive_PUT_admin_user(self):
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

    def test_url_users_detail_positive_PATCH_user(self):
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
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

    def test_url_users_detail_positive_PATCH_admin_self(self):
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

    def test_url_users_detail_positive_PATCH_admin_user(self):
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

    def test_url_users_detail_positive_DELETE_user(self):
        url = reverse('user-detail', args=[self.user.pk])
        response = self.client.delete(path=url, HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(path=url, HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        self.assertContains(response=response, text='User is inactive', status_code=status.HTTP_401_UNAUTHORIZED)

    def test_url_users_detail_positive_DELETE_admin_self(self):
        url = reverse('user-detail', args=[self.admin.pk])
        response = self.client.delete(path=url, HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.delete(path=url, HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        self.assertContains(response=response, text='User is inactive', status_code=status.HTTP_401_UNAUTHORIZED)

    def test_url_users_detail_positive_DELETE_admin_user(self):
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
    def setUp(self) -> None:
        self.second_user = CustomUser.objects.create_user(email='second@test.com', password='password')
        self.second_user.save()
        super(UsersDetailURLNegativeTestCase, self).setUp()

    def test_url_users_detail_negative_GET_unauthorized(self):
        url = reverse('user-detail', args=[self.user.pk])
        response = self.client.get(path=url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_url_users_detail_negative_GET_another_user(self):
        url = reverse('user-detail', args=[self.second_user.pk])
        response = self.client.get(path=url, HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_url_users_detail_negative_PUT_wrong_email_user(self):
        url = reverse('user-detail', args=[self.user.pk])
        input_data = {
            'email': self.second_user.email,
            'password': 'new password'
        }
        response = self.client.put(path=url, data=input_data, content_type='application/json',
                                   HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_url_users_detail_negative_PUT_wrong_email_admin(self):
        url = reverse('user-detail', args=[self.user.pk])
        input_data = {
            'email': self.second_user.email,
            'password': 'new password'
        }
        response = self.client.put(path=url, data=input_data, content_type='application/json',
                                   HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_url_users_detail_negative_PUT_not_all_fields(self):
        url = reverse('user-detail', args=[self.user.pk])
        data = {
            'email': 'changed_email@test.com'
        }
        response = self.client.put(path=url, data=data, content_type='application/json',
                                   HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UsersListURLPositiveTestCase(LoggedInTestCase):
    def setUp(self) -> None:
        self.url_list = reverse('user-list')
        self.another_user_credentials = {
            'email': 'another_email@test.com',
            'password': 'password',
        }
        super(UsersListURLPositiveTestCase, self).setUp()

    def test_url_users_list_positive_GET_user(self):
        response = self.client.get(path=self.url_list, HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        expected_result = {
            'id': self.user.pk,
            'email': self.user.email,
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data.get('results', None))
        data = response.data['results']
        self.assertEqual(len(data), 1)
        self.assertDictEqual(dict(data[0]), expected_result)

    def test_url_users_list_positive_GET_admin(self):
        response = self.client.get(path=self.url_list, HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
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

    def test_url_users_list_positive_POST_unauthorized(self):
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

    def test_url_users_list_positive_POST_admin(self):
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
