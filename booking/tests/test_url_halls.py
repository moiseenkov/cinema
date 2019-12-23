"""
Tests for endpoints:
 - /halls/
 - /halls/<int:pk>/
"""
from django.urls import reverse
from rest_framework import status

from booking.models import Hall
from booking.tests.helper import LoggedInTestCase


class HallsDetailPositiveTestCase(LoggedInTestCase):
    """
    Positive test case for hall detail: /halls/<int:pk>/
    """
    def test_url_halls_detail_positive_get(self):
        """
        Positive test checks response for GET request to /halls/<int:pk>/
        """
        hall = Hall(name='Test hall', rows_count=16, rows_size=32)
        hall.save()
        expected_response = {
            'id': hall.pk,
            'name': hall.name,
            'rows_count': hall.rows_count,
            'rows_size': hall.rows_size,
            'seats_count': hall.rows_count * hall.rows_size,
        }
        response = self.client.get(path=reverse('hall-detail', args=[hall.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, expected_response)

    def test_url_halls_detail_positive_put_admin(self):
        """
        Positive test checks response for admin's PUT request to /halls/<int:pk>/
        """
        input_data = {
            'name': 'Test name',
            'rows_count': 16,
            'rows_size': 16,
        }
        hall = Hall.objects.all().first()
        response = self.client.put(path=reverse('hall-detail', args=[hall.pk]),
                                   data=input_data,
                                   content_type='application/json',
                                   HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        expected_response = {
            'id': hall.pk,
            'name': input_data['name'],
            'rows_count': input_data['rows_count'],
            'rows_size': input_data['rows_size'],
            'seats_count': input_data['rows_count'] * input_data['rows_size'],
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, expected_response)

    def test_url_halls_detail_positive_patch_admin(self):
        """
        Positive test checks response for admin's PATCH request to /halls/<int:pk>/
        """
        hall = Hall(name='Name', rows_count=12, rows_size=20)
        hall.save()
        input_data = {
            'name': 'New name',
        }
        response = self.client.patch(path=reverse('hall-detail', args=[hall.pk]),
                                     data=input_data,
                                     content_type='application/json',
                                     HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        hall.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(hall.name, input_data['name'])
        self.assertEqual(response.data['name'], input_data['name'])

    def test_url_halls_detail_positive_delete_admin(self):
        """
        Positive test checks response for admin's DELETE request to /halls/<int:pk>/
        """
        hall = Hall(name='Name', rows_count=12, rows_size=20)
        hall.save()
        pkey = hall.pk
        response = self.client.delete(path=reverse('hall-detail', args=[pkey]),
                                      HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        halls = Hall.objects.filter(pk=pkey)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(halls.count(), 0)


class HallsDetailNegativeTestCase(LoggedInTestCase):
    """
    Negative test case for hall detail: /halls/<int:pk>/
    """
    def test_url_halls_detail_negative_get_unknown(self):
        """
        Negative test checks 404 status code on /halls/<not existing hall>
        """
        pkey = max(hall.pk for hall in Hall.objects.all()) + 1
        response = self.client.get(path=reverse('hall-detail', args=[pkey]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_url_halls_detail_negative_put_user(self):
        """
        Negative test checks that users cannot modify halls via PUT requests
        """
        input_data = {
            'name': 'Test name',
            'rows_count': 16,
            'rows_size': 16,
        }
        hall = Hall.objects.all().first()
        response = self.client.put(path=reverse('hall-detail', args=[hall.pk]),
                                   data=input_data,
                                   content_type='application/json',
                                   HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_url_halls_detail_negative_put_unauthorized(self):
        """
        Negative test checks that anonymous users cannot modify halls via PUT requests
        """
        input_data = {
            'name': 'Test name',
            'rows_count': 16,
            'rows_size': 16,
        }
        hall = Hall.objects.all().first()
        response = self.client.put(path=reverse('hall-detail', args=[hall.pk]), data=input_data,
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_url_halls_detail_negative_patch_user(self):
        """
        Negative test checks that users cannot modify halls via PATCH requests
        """
        hall = Hall(name='Name', rows_count=12, rows_size=20)
        hall.save()
        input_data = {
            'name': 'New name',
        }
        response = self.client.patch(path=reverse('hall-detail', args=[hall.pk]),
                                     data=input_data,
                                     content_type='application/json',
                                     HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        hall.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_url_halls_detail_negative_patch_unauthorized(self):
        """
        Negative test checks that anonymous users cannot modify halls via PATCH requests
        """
        hall = Hall(name='Name', rows_count=12, rows_size=20)
        hall.save()
        input_data = {
            'name': 'New name',
        }
        response = self.client.patch(path=reverse('hall-detail', args=[hall.pk]),
                                     data=input_data,
                                     content_type='application/json')
        hall.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_url_halls_detail_negative_patch_incorrect_input(self):
        """
        Negative test checks incorrect input while modifying halls
        """
        hall = Hall(name='Name', rows_count=12, rows_size=20)
        hall.save()

        with self.subTest():
            input_data = {
                'name': '',
            }
            response = self.client.patch(path=reverse('hall-detail', args=[hall.pk]),
                                         data=input_data,
                                         content_type='application/json',
                                         HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        with self.subTest():
            input_data = {
                'rows_count': 0,
            }
            response = self.client.patch(path=reverse('hall-detail', args=[hall.pk]),
                                         data=input_data,
                                         content_type='application/json',
                                         HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        with self.subTest():
            input_data = {
                'rows_size': 0,
            }
            response = self.client.patch(path=reverse('hall-detail', args=[hall.pk]),
                                         data=input_data,
                                         content_type='application/json',
                                         HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_url_halls_detail_negative_delete_user(self):
        """
        Negative test checks that users cannot delete halls
        """
        hall_data = {
            'name': 'Name',
            'rows_count': 12,
            'rows_size': 20,
        }
        hall = Hall(**hall_data)
        hall.save()
        pkey = hall.pk
        response = self.client.delete(path=reverse('hall-detail', args=[hall.pk]),
                                      HTTP_AUTHORIZATION=f'Bearer {self.user_token}')

        halls = Hall.objects.filter(pk=pkey)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(halls.count(), 1)
        hall = halls[0]
        self.assertEqual(hall.pk, pkey)
        self.assertEqual(hall.name, hall_data['name'])
        self.assertEqual(hall.rows_count, hall_data['rows_count'])
        self.assertEqual(hall.rows_size, hall_data['rows_size'])

    def test_url_halls_detail_negative_delete_unauthorized(self):
        """
        Negative test checks that anonymous users cannot delete halls
        """
        hall_data = {
            'name': 'Name',
            'rows_count': 12,
            'rows_size': 20,
        }
        hall = Hall(**hall_data)
        hall.save()
        pkey = hall.pk
        response = self.client.delete(path=reverse('hall-detail', args=[hall.pk]))

        halls = Hall.objects.filter(pk=pkey)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(halls.count(), 1)
        hall = halls[0]
        self.assertEqual(hall.pk, pkey)
        self.assertEqual(hall.name, hall_data['name'])
        self.assertEqual(hall.rows_count, hall_data['rows_count'])
        self.assertEqual(hall.rows_size, hall_data['rows_size'])


class HallsListPositiveTestCase(LoggedInTestCase):
    """
    Positive test case for halls list: /halls/
    """
    def setUp(self) -> None:
        self.url_list = reverse('hall-list')
        super(HallsListPositiveTestCase, self).setUp()

    def test_url_hall_list_positive_get(self):
        """
        Positive test checks response for GET request to /halls/
        """
        sub_test_parameters = [
            {
                # Unauthorized user
                'path': self.url_list,
            },
            {
                # Authorized user
                'path': self.url_list,
                'HTTP_AUTHORIZATION': f'Bearer {self.user_token}',
            },
            {
                # Admin
                'path': self.url_list,
                'HTTP_AUTHORIZATION': f'Bearer {self.admin_token}',
            },
        ]
        expected_response = [
            {
                'id': hall.pk,
                'name': hall.name,
                'rows_count': hall.rows_count,
                'rows_size': hall.rows_size,
                'seats_count': hall.rows_count * hall.rows_size,
            } for hall in Hall.objects.all().order_by('-pk')
        ]
        for request_parameter_set in sub_test_parameters:
            with self.subTest(request_parameter_Set=request_parameter_set):
                response = self.client.get(**request_parameter_set)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertIsNotNone(response.data.get('results', None))
                for received, expected in zip(response.data['results'], expected_response):
                    self.assertDictEqual(dict(received), expected)

    def test_url_hall_list_positive_post_admin(self):
        """
        Positive test checks response for admin's POST request to /halls/
        """
        data = {
            'name': 'Name',
            'rows_count': 16,
            'rows_size': 26,
        }
        response = self.client.post(path=self.url_list,
                                    data=data,
                                    HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        halls = Hall.objects.filter(name=data['name'])

        self.assertEqual(halls.count(), 1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        hall = halls[0]
        expected_response = data.copy()
        expected_response['id'] = hall.pk
        expected_response['seats_count'] = data['rows_count'] * data['rows_size']
        self.assertDictEqual(response.data, expected_response)


class HallsListNegativeTestCase(LoggedInTestCase):
    """
    Negative test case for halls list: /halls/
    """
    def setUp(self) -> None:
        self.url_list = reverse('hall-list')
        super(HallsListNegativeTestCase, self).setUp()

    def test_url_hall_list_negative_post_unauthorized(self):
        """
        Negative test checks that anonymous users cannot create halls
        """
        data = {
            'name': 'Name',
            'rows_count': 16,
            'rows_size': 26,
        }
        response = self.client.post(path=self.url_list)
        halls = Hall.objects.filter(name=data['name'])

        self.assertEqual(halls.count(), 0)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_url_hall_list_negative_post_user(self):
        """
        Negative test checks that users cannot create halls
        """
        data = {
            'name': 'Name',
            'rows_count': 16,
            'rows_size': 26,
        }
        response = self.client.post(path=self.url_list,
                                    HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        halls = Hall.objects.filter(name=data['name'])

        self.assertEqual(halls.count(), 0)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_url_hall_list_negative_post_incorrect_input(self):
        """
        Negative test checks incorrect input while creating halls
        """
        cases = [
            {
                'name': 'Name',
                'rows_count': 16,
            },
            {
                'name': 'Name',
                'rows_size': 16,
            },
            {
                'rows_size': 16,
                'rows_count': 16,
            },
            {
                'name': '',
                'rows_count': '',
                'rows_size': '',
            },
            {
                'name': 'Name',
                'rows_count': -10,
                'rows_size': 26,
            },
            {
                'name': 'Name',
                'rows_count': 10,
                'rows_size': 0,
            },
        ]
        halls_control = list(Hall.objects.all().order_by('-pk'))
        for case in cases:
            with self.subTest(case=case):
                response = self.client.post(path=self.url_list, data=case,
                                            HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
                halls = list(Hall.objects.all().order_by('-pk'))

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertEqual(len(halls_control), len(halls))
                for received, expected in zip(halls_control, halls):
                    self.assertEqual(received.pk, expected.pk)
                    self.assertEqual(received.name, expected.name)
                    self.assertEqual(received.rows_count, expected.rows_count)
                    self.assertEqual(received.rows_size, expected.rows_size)
