"""
Tests for endpoints:
 - /showings/
 - /showings/<int:pk>/
"""
import datetime

from django.urls import reverse
from rest_framework import status

from booking.models import Movie, Hall, Showing
from booking.tests.helper import LoggedInTestCase


class ShowingsBaseTestCase(LoggedInTestCase):
    """
    Base test case prepares movie and hall instances for test showings
    """

    def setUp(self) -> None:
        self.movie = Movie(name='Movie', duration=120, premiere_year=1999)
        self.movie.save()
        self.hall = Hall(name='Hall', rows_count=16, rows_size=20)
        self.hall.save()
        super(ShowingsBaseTestCase, self).setUp()


class ShowingsDetailPositiveTestCase(ShowingsBaseTestCase):
    """
    Positive test case for showing detail: /showings/<int:pk>/
    """

    def test_url_showings_detail_positive_get(self):
        """
        Positive test checks response for GET request to /showings/<int:pk>/
        """
        showing = Showing(hall=self.hall, movie=self.movie,
                          date_time=datetime.datetime(2019, 11, 25, 9, 0, 0, 1,
                                                      tzinfo=datetime.timezone.utc),
                          price='9.99')
        showing.save()

        expected_response = {
            'id': showing.pk,
            'hall': self.hall.pk,
            'movie': self.movie.pk,
            'price': showing.price,
            'date_time': showing.date_time.isoformat()[:-3] + showing.date_time.isoformat()[-2:],
        }
        response = self.client.get(path=reverse('showing-detail', args=[showing.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, expected_response)

    def test_url_showings_detail_positive_put_admin(self):
        """
        Positive test checks response for admin's PUT request to /showings/<int:pk>/
        """
        showing = Showing(hall=self.hall, movie=self.movie,
                          date_time=datetime.datetime(2019, 11, 25, 9, 0, 10, 10,
                                                      tzinfo=datetime.timezone.utc),
                          price='9.99')
        showing.save()

        input_data = {
            'hall': showing.hall.pk,
            'movie': showing.movie.pk,
            'date_time': showing.date_time.isoformat(),
            'price': '4.99'
        }
        response = self.client.put(path=reverse('showing-detail', args=[showing.pk]),
                                   data=input_data,
                                   content_type='application/json',
                                   HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        expected_response = {
            'id': showing.pk,
            'hall': self.hall.pk,
            'movie': self.movie.pk,
            'price': input_data['price'],
            'date_time': showing.date_time.isoformat()[:-3] + showing.date_time.isoformat()[-2:],
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, expected_response)

    def test_url_showings_detail_positive_patch_admin(self):
        """
        Positive test checks response for admin's PATCH request to /showings/<int:pk>/
        """
        showing = Showing(hall=self.hall, movie=self.movie,
                          date_time=datetime.datetime(2019, 11, 25, 9, 0, 0, 1,
                                                      tzinfo=datetime.timezone.utc),
                          price='9.99')
        showing.save()

        input_data = {
            'price': '4.99'
        }
        response = self.client.patch(path=reverse('showing-detail', args=[showing.pk]),
                                     data=input_data,
                                     content_type='application/json',
                                     HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        expected_response = {
            'id': showing.pk,
            'hall': self.hall.pk,
            'movie': self.movie.pk,
            'price': input_data['price'],
            'date_time': showing.date_time.isoformat()[:-3] + showing.date_time.isoformat()[-2:],
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, expected_response)

    def test_url_showings_detail_positive_delete_admin(self):
        """
        Positive test checks response for admin's DELETE request to /showings/<int:pk>/
        """
        showing = Showing(hall=self.hall, movie=self.movie,
                          date_time=datetime.datetime(2019, 11, 25, 9, 0,
                                                      tzinfo=datetime.timezone.utc),
                          price='9.99')
        showing.save()
        response = self.client.delete(path=reverse('showing-detail', args=[showing.pk]),
                                      content_type='application/json',
                                      HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class ShowingsDetailNegativeTestCase(ShowingsBaseTestCase):
    """
    Negative test case for showing detail: /showings/<int:pk>/
    """

    def setUp(self) -> None:
        super(ShowingsDetailNegativeTestCase, self).setUp()
        self.showing = Showing(hall=self.hall, movie=self.movie,
                               date_time=datetime.datetime(2019, 12, 14, 10, 0,
                                                           tzinfo=datetime.timezone.utc),
                               price=9.99)
        self.showing.save()

    def test_url_showings_detail_negative_get_unknown(self):
        """
        Negative test checks 404 status code on /showings/<not existing hall>
        """
        response = self.client.get(path=reverse('showing-detail', args=[100]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_url_showings_detail_negative_put_user(self):
        """
        Negative test checks that users cannot modify showings via PUT requests
        """
        input_data = {
            'price': 2.0,
        }
        response = self.client.put(path=reverse('showing-detail', args=[self.showing.pk]),
                                   data=input_data,
                                   content_type='application/json',
                                   HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_url_showings_detail_negative_put_unauthorized(self):
        """
        Negative test checks that anonymous users cannot modify showings via PUT requests
        """
        input_data = {
            'date_time': datetime.datetime.now(tz=datetime.timezone.utc),
            'hall': self.hall.pk + 1,
            'movie': self.movie.pk + 1,
            'price': 2.0
        }
        response = self.client.put(path=reverse('movie-detail', args=[self.showing.pk]),
                                   data=input_data,
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_url_showing_detail_negative_patch_user(self):
        """
        Negative test checks that users cannot modify showing via PATCH requests
        """
        input_data = {
            'date_time': datetime.datetime.now(tz=datetime.timezone.utc),
            'hall': self.hall.pk + 1,
            'movie': self.movie.pk + 1,
            'price': 2.0
        }
        response = self.client.patch(path=reverse('showing-detail', args=[self.showing.pk]),
                                     data=input_data,
                                     content_type='application/json',
                                     HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_url_showings_detail_negative_patch_unauthorized(self):
        """
        Negative test checks that anonymous users cannot modify showings via PATCH requests
        """
        input_data = {
            'date_time': datetime.datetime.now(tz=datetime.timezone.utc),
            'hall': self.hall.pk + 1,
            'movie': self.movie.pk + 1,
            'price': 2.0
        }
        response = self.client.patch(path=reverse('showing-detail', args=[self.showing.pk]),
                                     data=input_data,
                                     content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_url_showing_detail_negative_patch_incorrect_input(self):
        """
        Negative test checks incorrect input while modifying showings
        """
        incorrect_date =\
            datetime.datetime(self.showing.movie.premiere_year, 1, 1, 10, 0,
                              tzinfo=datetime.timezone.utc) - datetime.timedelta(20)
        input_data = {
            'date_time': incorrect_date.isoformat()
        }
        response = self.client.patch(path=reverse('showing-detail', args=[self.showing.pk]),
                                     data=input_data,
                                     content_type='application/json',
                                     HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_url_showings_detail_negative_delete_user(self):
        """
        Negative test checks that users cannot delete showings
        """
        response = self.client.delete(path=reverse('showing-detail', args=[self.showing.pk]),
                                      HTTP_AUTHORIZATION=f'Bearer {self.user_token}')

        self.showing.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Showing.objects.all().count(), 1)

    def test_url_showings_detail_negative_delete_unauthorized(self):
        """
        Negative test checks that anonymous users cannot delete showings
        """
        response = self.client.delete(path=reverse('movie-detail', args=[self.showing.pk]))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Showing.objects.all().count(), 1)


class ShowingsListPositiveTestCase(ShowingsBaseTestCase):
    """
    Positive test case for showings list: /showings/
    """
    def setUp(self) -> None:
        super(ShowingsListPositiveTestCase, self).setUp()
        self.url_list = reverse('showing-list')
        showings = [Showing(hall_id=hall_id, movie=self.movie,
                            date_time=datetime.datetime(2019, 12, 14, 10, 0, 0, 1,
                                                        tzinfo=datetime.timezone.utc).isoformat(),
                            price=9.99) for hall_id in [1, 2, 3]]
        Showing.objects.bulk_create(showings)
        self.showings = list(Showing.objects.all())

    def test_url_showing_list_positive_get(self):
        """
        Positive test checks response for GET request to /showings/
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
                'id': showing.pk,
                'movie': showing.movie.pk,
                'hall': showing.hall.pk,
                'price': str(showing.price),
                'date_time': showing.date_time.isoformat()[:-3] + showing.date_time.isoformat()[-2:]
            } for showing in Showing.objects.all().order_by('pk')
        ]
        for request_parameter_set in sub_test_parameters:
            with self.subTest(request_parameter_Set=request_parameter_set):
                response = self.client.get(**request_parameter_set)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertIsNotNone(response.data.get('results', None))
                for received, expected in zip(response.data['results'], expected_response):
                    self.assertDictEqual(dict(received), expected)

    def test_url_showing_list_positive_post_admin(self):
        """
        Positive test checks response for admin's POST request to /showing/
        """
        data = {
            'movie': self.movie.pk,
            'hall': self.hall.pk,
            'price': '199.90',
            'date_time': self.showings[0].date_time + datetime.timedelta(7)
        }
        response = self.client.post(path=self.url_list,
                                    data=data,
                                    HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        showings = Showing.objects.filter(price=data['price'])

        self.assertEqual(showings.count(), 1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        showing = showings[0]
        expected_response = data.copy()
        expected_response['id'] = showing.pk
        expected_response['date_time'] = \
            expected_response['date_time'].isoformat()[:-3] + \
            expected_response['date_time'].isoformat()[-2:]
        self.assertDictEqual(response.data, expected_response)


class ShowingsListNegativeTestCase(ShowingsBaseTestCase):
    """
    Negative test case for showings list: /showings/
    """
    def setUp(self) -> None:
        super(ShowingsListNegativeTestCase, self).setUp()
        self.url_list = reverse('showing-list')
        showings = [Showing(hall_id=hall_id, movie=self.movie,
                            date_time=datetime.datetime(2019, 12, 14, 10, 0,
                                                        tzinfo=datetime.timezone.utc).isoformat(),
                            price=9.99) for hall_id in [1, 2, 3]]
        Showing.objects.bulk_create(showings)
        self.showings = list(Showing.objects.all())

    def test_url_showing_list_negative_post_unauthorized(self):
        """
        Negative test checks that anonymous users cannot create showing
        """
        data = {
            'hall': self.hall.pk,
            'movie': self.movie.pk,
            'price': '199.99',
            'date_time': datetime.datetime(2019, 12, 14, 10, 0,
                                           tzinfo=datetime.timezone.utc).isoformat(),
        }
        response = self.client.post(path=self.url_list)
        movies = Showing.objects.filter(price=data['price'])

        self.assertEqual(movies.count(), 0)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_url_showing_list_negative_post_user(self):
        """
        Negative test checks that users cannot create showings
        """
        data = {
            'hall': self.hall.pk,
            'movie': self.movie.pk,
            'price': '199.99',
            'date_time': datetime.datetime(2019, 12, 14, 10, 0,
                                           tzinfo=datetime.timezone.utc).isoformat(),
        }
        response = self.client.post(path=self.url_list,
                                    HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        movies = Showing.objects.filter(price=data['price'])

        self.assertEqual(movies.count(), 0)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_url_showing_list_negative_post_incorrect_input(self):
        """
        Negative test checks incorrect input while creating showings
        """
        incorrect_date = datetime.datetime(self.movie.premiere_year, 1, 1, 10, 0,
                                           tzinfo=datetime.timezone.utc) - datetime.timedelta(20)
        data = {
            'hall': self.hall.pk,
            'movie': self.movie.pk,
            'price': '199.99',
            'date_time': incorrect_date.isoformat(),
        }
        showings_control = list(Showing.objects.all().order_by('-pk'))
        response = self.client.post(path=self.url_list, data=data,
                                    HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        showings = list(Showing.objects.all().order_by('-pk'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(showings_control), len(showings))
