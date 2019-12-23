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
                          date_time=datetime.datetime(2019, 11, 25, 9, 0,
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
                          date_time=datetime.datetime(2019, 11, 25, 9, 0,
                                                      tzinfo=datetime.timezone.utc),
                          price='9.99')
        showing.save()

        input_data = {
            'hall': showing.hall.pk,
            'movie': showing.movie.pk,
            'date_time': showing.date_time,
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
                          date_time=datetime.datetime(2019, 11, 25, 9, 0,
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


class ShowingsListPositiveTestCase(ShowingsBaseTestCase):
    """
    Positive test case for showings list: /showings/
    """


class ShowingsListNegativeTestCase(ShowingsBaseTestCase):
    """
    Negative test case for showings list: /showings/
    """
