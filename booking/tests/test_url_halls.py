from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from booking.models import Hall
from booking.tests import helper
from booking.tests.helper import LoggedInUserTestCase, LoggedInAdminTestCase


class TestURLHalls(TestCase):
    def setUp(self) -> None:
        self.url_list = reverse('hall-list')
        self.halls = helper.get_halls_dict()

    def test_url_halls_get_list(self):
        response = self.client.get(path=self.url_list, data={})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data.get('results', None))
        self.assertEqual(len(response.data['results']), len(self.halls))
        for expected in self.halls:
            with self.subTest(expected=expected):
                halls_found = [hall_ for hall_ in response.data['results'] if hall_['id'] == expected['id']]
                self.assertEqual(len(halls_found), 1)
                self.assertSetEqual(set(expected.items()), set(halls_found[0].items()))

    def test_url_halls_get_detail(self):
        for hall in self.halls:
            with self.subTest(hall=hall):
                response = self.client.get(path=reverse('hall-detail', args=[hall['id']]), data={})
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertIsInstance(response.data, dict)
                self.assertDictEqual(response.data, hall)

    def test_url_halls_post(self):
        data = {
            'name': 'New name'
        }
        response = self.client.post(path=self.url_list, data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_url_halls_put_patch_delete(self):
        hall = self.halls[0]
        url = reverse('hall-detail', args=[hall['id']])
        data = {
            'name': 'Changed name by unauthorised user'
        }

        with self.subTest():
            response = self.client.put(path=url, data=data)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        with self.subTest():
            response = self.client.patch(path=url, data=data)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        with self.subTest():
            response = self.client.delete(path=url, data=data)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestURLHallsUser(LoggedInUserTestCase):
    def setUp(self) -> None:
        self.halls = helper.get_halls_dict()
        super(TestURLHallsUser, self).setUp()

    def test_url_halls_get_list(self):
        response = self.client.get(path=reverse('hall-list'), data={}, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data.get('results', None))
        self.assertEqual(len(response.data['results']), len(self.halls))
        for expected in self.halls:
            with self.subTest(expected=expected):
                halls_found = [hall_ for hall_ in response.data['results'] if hall_['id'] == expected['id']]
                self.assertEqual(len(halls_found), 1)
                self.assertSetEqual(set(expected.items()), set(halls_found[0].items()))

    def test_url_halls_get_detail(self):
        for hall in self.halls:
            with self.subTest(hall=hall):
                response = self.client.get(path=reverse('hall-detail', args=[hall['id']]), data={},
                                           HTTP_AUTHORIZATION=f'Bearer {self.token}')
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertIsInstance(response.data, dict)
                self.assertDictEqual(response.data, hall)

    def test_url_halls_post(self):
        data = {
            'name': 'New name'
        }
        response = self.client.post(path=reverse('hall-list'), data=data, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_url_halls_put_patch_delete(self):
        hall = self.halls[0]
        url = reverse('hall-detail', args=[hall['id']])
        data = {
            'name': 'Changed name by unauthorised user'
        }

        with self.subTest():
            response = self.client.put(path=url, data=data, HTTP_AUTHORIZATION=f'Bearer {self.token}')
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        with self.subTest():
            response = self.client.patch(path=url, data=data, HTTP_AUTHORIZATION=f'Bearer {self.token}')
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        with self.subTest():
            response = self.client.delete(path=url, data=data, HTTP_AUTHORIZATION=f'Bearer {self.token}')
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestURLHallsAdmin(LoggedInAdminTestCase):
    def setUp(self) -> None:
        super(TestURLHallsAdmin, self).setUp()
        self.new_hall_name = 'Test cinema hall'
        self.new_hall_data = {
            'name': self.new_hall_name,
            'rows_count': 10,
            'rows_size': 10
        }

    def test_url_halls_put(self):
        hall = Hall.objects.all().first()
        self.assertIsNotNone(hall)

        data = {
            'name': 'Changed name'
        }
        response = self.client.put(path=reverse('hall-detail', args=[hall.pk]), data=data,
                                   content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data['rows_count'] = -10
        data['rows_size'] = -10
        response = self.client.put(path=reverse('hall-detail', args=[hall.pk]), data=data,
                                   content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data['rows_count'] = 1001
        data['rows_size'] = 1001
        response = self.client.put(path=reverse('hall-detail', args=[hall.pk]), data=data,
                                   content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {self.token}')
        data['id'] = hall.pk
        data['seats_count'] = data['rows_count'] * data['rows_size']
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, data)

    def test_url_halls_post(self):
        response = self.client.post(path=reverse('hall-list'), data=self.new_hall_data,
                                    HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_hall = Hall.objects.filter(name=self.new_hall_name).first()
        self.assertIsNotNone(new_hall)

        expected_data = self.new_hall_data.copy()
        expected_data['id'] = new_hall.pk
        expected_data['seats_count'] = 10 * 10
        self.assertDictEqual(response.data, expected_data)

    def test_url_halls_post_empty(self):
        response = self.client.post(path=reverse('hall-list'), data={},
                                    HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_url_halls_post_already_exist(self):
        hall = Hall(**self.new_hall_data)
        hall.save()
        response = self.client.post(path=reverse('hall-list'), data=self.new_hall_data,
                                    HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_url_halls_patch(self):
        hall = Hall.objects.all().first()
        self.assertIsNotNone(hall)

        changed_name = 'Changed name'
        data = {
            'name': changed_name
        }
        response = self.client.patch(path=reverse('hall-detail', args=[hall.pk]), data=data,
                                     content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data.get('name', None))
        self.assertEqual(response.data['name'], changed_name)

    def test_url_halls_patch_already_exist(self):
        halls = Hall.objects.all()
        self.assertGreaterEqual(halls.count(), 2)
        hall1, hall2 = halls[0], halls[1]

        data = {
            'name': hall2.name
        }
        response = self.client.patch(path=reverse('hall-detail', args=[hall1.pk]), data=data,
                                     content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_url_halls_delete(self):
        hall = Hall.objects.all().first()
        self.assertIsNotNone(hall)

        response = self.client.delete(path=reverse('hall-detail', args=[hall.pk]),
                                      HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.delete(path=reverse('hall-detail', args=[hall.pk]),
                                      HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
