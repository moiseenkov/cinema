"""
Tests for endpoints:
 - /tickets/
 - /tickets/<int:pk>/
"""
import datetime
from decimal import Decimal

from django.urls import reverse
from rest_framework import status

from booking.models import Showing, Hall, Movie, Ticket
from booking.tests.helper import LoggedInTestCase


class TicketsBaseTestCase(LoggedInTestCase):
    """
    Base test case prepares movie and hall instances for test tickets
    """

    def setUp(self) -> None:
        super(TicketsBaseTestCase, self).setUp()
        self.movie = Movie(name='Movie', duration=120, premiere_year=1999)
        self.movie.save()
        self.hall = Hall(name='Hall', rows_count=16, rows_size=20)
        self.hall.save()
        show_time = \
            datetime.datetime(2019, 12, 24, 10, 0, tzinfo=datetime.timezone.utc) + \
            datetime.timedelta(10)
        self.showing = Showing(hall=self.hall,
                               movie=self.movie,
                               date_time=show_time,
                               price='19.99')
        self.showing.save()
        ticket_time = show_time - datetime.timedelta(10)
        self.ticket = Ticket(showing=self.showing,
                             user=self.user,
                             date_time=ticket_time,
                             row_number=1, seat_number=1)
        self.ticket.save()


class TicketsDetailPositiveTestCase(TicketsBaseTestCase):
    """
    Positive test case for ticket detail: /tickets/<int:pk>/
    """

    def test_url_tickets_detail_positive_get_user(self):
        """
        Positive test checks response for GET request to /tickets/<int:pk>/
        """
        ticket = self.ticket
        expected_response = {
            'id': ticket.pk,
            'showing': ticket.showing.pk,
            'date_time': ticket.date_time.isoformat()[:-3] + ticket.date_time.isoformat()[-2:],
            'row_number': ticket.row_number,
            'seat_number': ticket.seat_number,
            'paid': False,
            'price': Decimal(ticket.showing.price),
            'receipt': '',
            'user': self.user.pk,
        }
        response = self.client.get(path=reverse('ticket-detail', args=[ticket.pk]),
                                   HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, expected_response)

    def test_url_tickets_detail_positive_put_admin(self):
        """
        Positive test checks response for admin's PUT request to /tickets/<int:pk>/
        """
        ticket = self.ticket
        input_data = {
            'showing': ticket.showing.pk,
            'date_time': ticket.date_time.isoformat()[:-3] + ticket.date_time.isoformat()[-2:],
            'row_number': 2,
            'seat_number': 2,
            'paid': False,
            'receipt': '',
            'user': self.user.pk,
        }
        response = self.client.put(path=reverse('ticket-detail', args=[ticket.pk]),
                                   data=input_data,
                                   content_type='application/json',
                                   HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        expected_response = {
            'id': ticket.pk,
            'showing': ticket.showing.pk,
            'date_time': ticket.date_time.isoformat()[:-3] + ticket.date_time.isoformat()[-2:],
            'row_number': 2,
            'seat_number': 2,
            'paid': False,
            'receipt': '',
            'user': self.user.pk,
            'price': Decimal(self.showing.price),
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, expected_response)

    def test_url_tickets_detail_positive_patch_admin(self):
        """
        Positive test checks response for admin's PATCH request to /tickets/<int:pk>/
        """
        input_data = {
            'row_number': '2',
            'seat_number': '2',
        }
        response = self.client.patch(path=reverse('ticket-detail', args=[self.ticket.pk]),
                                     data=input_data,
                                     content_type='application/json',
                                     HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        ticket = self.ticket
        expected_response = {
            'id': ticket.pk,
            'showing': ticket.showing.pk,
            'date_time': ticket.date_time.isoformat()[:-3] + ticket.date_time.isoformat()[-2:],
            'row_number': 2,
            'seat_number': 2,
            'paid': False,
            'receipt': '',
            'user': self.user.pk,
            'price': Decimal(self.showing.price),
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, expected_response)

    def test_url_tickets_detail_positive_delete_admin(self):
        """
        Positive test checks response for admin's DELETE request to /tickets/<int:pk>/
        """
        response = self.client.delete(path=reverse('ticket-detail', args=[self.ticket.pk]),
                                      content_type='application/json',
                                      HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Ticket.objects.all().count(), 0)


class TicketsDetailNegativeTestCase(TicketsBaseTestCase):
    """
    Negative test case for ticket detail: /tickets/<int:pk>/
    """
    def test_url_tickets_detail_negative_get_unknown(self):
        """
        Negative test checks that unauthorized users have no access to tickets
        """
        with self.subTest():
            response = self.client.get(path=reverse('ticket-detail', args=[self.ticket.pk]))
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        with self.subTest():
            response = self.client.get(path=reverse('ticket-detail', args=[1000]))
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_url_tickets_detail_negative_put_user(self):
        """
        Negative test checks that users can modify only their seats via PUT requests
        """
        input_data = {
            'showing': self.ticket.showing.pk + 1,
            'user': self.admin.pk,
            'date_time': self.ticket.date_time - datetime.timedelta(3),
            'row_number': 2,
            'seat_number': 2,
            'receipt': 'Fake receipt',
            'paid': True,
        }
        date_time = self.ticket.date_time.isoformat()[:-3] + self.ticket.date_time.isoformat()[-2:]
        expected_data = {
            'id': self.ticket.pk,
            'showing': self.ticket.showing.pk,
            'row_number': 2,
            'seat_number': 2,
            'price': Decimal(self.ticket.showing.price),
            'user': self.ticket.user.pk,
            'date_time': date_time,
            'paid': False,
            'receipt': self.ticket.receipt,
        }
        response = self.client.put(path=reverse('ticket-detail', args=[self.ticket.pk]),
                                   data=input_data,
                                   content_type='application/json',
                                   HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, expected_data)

    def test_url_tickets_detail_negative_put_unauthorized(self):
        """
        Negative test checks that anonymous users cannot modify tickets via PUT requests
        """
        input_data = {
            'showing': self.ticket.showing.pk + 1,
            'user': self.admin.pk,
            'date_time': self.ticket.date_time - datetime.timedelta(3),
            'row_number': 2,
            'seat_number': 2,
            'receipt': 'Fake receipt',
            'paid': True,
        }
        response = self.client.put(path=reverse('ticket-detail', args=[self.ticket.pk]),
                                   data=input_data,
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_url_ticket_detail_negative_patch_incorrect_input(self):
        """
        Negative test checks that users cannot book not existing place
        """
        input_data = {
            'row_number': self.ticket.showing.hall.rows_count + 100,
        }
        response = self.client.patch(path=reverse('ticket-detail', args=[self.ticket.pk]),
                                     data=input_data,
                                     content_type='application/json',
                                     HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_url_ticket_detail_negative_patch_unauthorized(self):
        """
        Negative test checks that anonymous users cannot modify tickets via PATCH requests
        """
        input_data = {
            'row_number': self.ticket.showing.hall.rows_count + 100,
        }
        response = self.client.patch(path=reverse('ticket-detail', args=[self.ticket.pk]),
                                     data=input_data,
                                     content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_url_tickets_detail_negative_delete_user(self):
        """
        Negative test checks that users cannot delete someone's else ticket
        """
        ticket = Ticket(showing=self.ticket.showing,
                        user=self.admin,
                        row_number=2,
                        seat_number=2,
                        date_time=self.ticket.date_time)
        ticket.save()
        response = self.client.delete(path=reverse('ticket-detail', args=[ticket.pk]),
                                      HTTP_AUTHORIZATION=f'Bearer {self.user_token}')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Ticket.objects.all().count(), 2)
        ticket.delete()

    def test_url_tickets_detail_negative_delete_unauthorized(self):
        """
        Negative test checks that anonymous users cannot delete tickets
        """
        response = self.client.delete(path=reverse('ticket-detail', args=[self.ticket.pk]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Ticket.objects.all().count(), 1)

    def test_url_tickets_detail_negative_delete_paid_ticket(self):
        """
        Negative test checks that it's impossible to delete paid ticket
        """
        self.ticket.receipt = 'receipt'
        self.ticket.save()

        response = self.client.delete(path=reverse('ticket-detail', args=[self.ticket.pk]),
                                      HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        self.assertEqual(response.status_code, status.HTTP_423_LOCKED)
