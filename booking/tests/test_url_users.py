import json

from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from booking.models import CustomUser
from booking.tests.helper import LoggedInUserTestCase


class TestURLUsersNotAuthenticated(TestCase):
    def setUp(self) -> None:
        self.url_list = reverse('user-list')
        self.credentials = {
                'email': 'user1@test.com',
                'password': 'password1'
            }

    def examine_response_is_ok(self, response):
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data.get('results', None))

    def test_users_list_get_empty(self):
        response = self.client.get(path=self.url_list, data={})
        self.examine_response_is_ok(response)
        self.assertEqual(response.data['results'], [])

    def test_users_list_get_not_empty(self):
        user = CustomUser.objects.create_user(**self.credentials)
        user.save()

        response = self.client.get(path=self.url_list, data={})
        self.examine_response_is_ok(response)
        self.assertEqual(response.data['results'], [])

    def test_user_detail_get(self):
        detail_url = reverse('user-detail', args=[1])
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        user = CustomUser.objects.create_user(**self.credentials)
        user.save()

        response = self.client.get(path=reverse('user-detail', args=[user.pk]), data={})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_detail_post(self):
        response = self.client.post(path=self.url_list, data=self.credentials)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertSetEqual(set(response.data.keys()), {'id', 'email', 'password'})
        self.assertEqual(response.data['email'], self.credentials['email'])

    def test_user_detail_put(self):
        user = CustomUser.objects.create_user(**self.credentials)
        user.save()

        response = self.client.put(path=reverse('user-detail', args=[user.pk]), data={})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.put(path=reverse('user-detail', args=[1000]), data={})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_detail_patch(self):
        user = CustomUser.objects.create_user(**self.credentials)
        user.save()

        response = self.client.put(path=reverse('user-detail', args=[user.pk]), data={})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.put(path=reverse('user-detail', args=[1000]), data={})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_detail_delete(self):
        user = CustomUser.objects.create_user(**self.credentials)
        user.save()

        response = self.client.delete(path=reverse('user-detail', args=[user.pk]), data={})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.delete(path=reverse('user-detail', args=[1000]), data={})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestURLUsersList(LoggedInUserTestCase):
    """
    Test case covers user's list usage for authenticated non staff users
    """

    def setUp(self) -> None:
        super(TestURLUsersList, self).setUp()
        self.user_list = reverse('user-list')
        self.new_user_credentials = {
            'email': 'new_user@test.com',
            'password': 'test'
        }

    def test_users_list_GET(self):
        response = self.client.get(path=self.user_list, data={}, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        expected_response = {
            "links": {
                "next": None,
                "previous": None
            },
            "count": 1,
            "total_pages": 1,
            "page_size": 10,
            "results": [
                {
                    "id": self.user.pk,
                    "email": self.user.email
                }
            ]
        }
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.data, expected_response)

        # User creates another user but he must not see him, thus list recall shouldn't change response body
        self.client.post(path=self.user_list, data=self.new_user_credentials,
                         HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client.get(path=self.user_list, data={}, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.data, expected_response)

    def test_users_list_POST(self):
        # create new user
        response = self.client.post(path=self.user_list, data=self.new_user_credentials,
                                    HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data.get('email', None), self.new_user_credentials['email'])
        new_user_id = response.data.get('id', None)

        # login as a new user
        response = self.client.post(path=reverse('token'), data=self.new_user_credentials)
        token = response.data.get('access', None)

        # check users list for new user
        expected_response = {
            "links": {
                "next": None,
                "previous": None
            },
            "count": 1,
            "total_pages": 1,
            "page_size": 10,
            "results": [
                {
                    "id": new_user_id,
                    "email": self.new_user_credentials['email']
                }
            ]
        }
        response = self.client.get(path=self.user_list, data={}, HTTP_AUTHORIZATION=f'Bearer {token}')
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.data, expected_response)


class TestURLUserDetail(LoggedInUserTestCase):
    def setUp(self) -> None:
        super(TestURLUserDetail, self).setUp()
        self.user_detail = reverse('user-detail', args=[self.user.pk])

    def test_user_detail_get(self):
        response = self.client.get(path=self.user_detail, data={}, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        expected_response = {
            'id': self.user.pk,
            'email': self.user.email
        }
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.data, expected_response)

        self.user.is_active = False
        self.user.save()
        response = self.client.get(path=self.user_detail, data={}, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, 401)

    def test_user_detail_get_wrong_id(self):
        url = reverse('user-detail', args=[10001])
        response = self.client.get(path=url, data={}, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertContains(response=response, text='Not found', status_code=404)

    def test_user_detail_put_patch(self):
        data = {
            'email': 'changed_email@test.com'
        }
        expected_response = {
            'id': self.user.pk,
            'email': data['email']
        }
        response = self.client.put(path=self.user_detail, data=json.dumps(data), content_type='application/json',
                                   HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.data, expected_response)

        response = self.client.patch(path=self.user_detail, data=json.dumps(data), content_type='application/json',
                                     HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.data, expected_response)

    def test_user_detail_put_patch_empty(self):
        response = self.client.put(path=self.user_detail, data={}, content_type='application/json',
                                   HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertContains(response=response, text='This field is required', status_code=400)
        self.assertContains(response=response, text='email', status_code=400)

        expected_response = {
            'id': self.user.pk,
            'email': self.user.email
        }
        response = self.client.patch(path=self.user_detail, data={}, content_type='application/json',
                                     HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.data, expected_response)

    def test_user_detail_put_patch_invalid_email(self):
        emails = ['second_user@test.com', 'incorrect email']
        user = CustomUser.objects.create_user(email=emails[0], password='password')
        user.save()
        for email in emails:
            with self.subTest(email=email):
                data = {
                    'email': email
                }
                response = self.client.put(path=self.user_detail, data=json.dumps(data),
                                           content_type='application/json',
                                           HTTP_AUTHORIZATION=f'Bearer {self.token}')
                self.assertEqual(response.status_code, 400)

                response = self.client.patch(path=self.user_detail, data=json.dumps(data),
                                             content_type='application/json',
                                             HTTP_AUTHORIZATION=f'Bearer {self.token}')
                self.assertEqual(response.status_code, 400)

    def test_user_detail_delete(self):
        response = self.client.delete(path=self.user_detail, data={}, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, 204)

        response = self.client.get(path=self.user_detail, data={}, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, 401)
