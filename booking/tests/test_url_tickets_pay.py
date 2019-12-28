"""
Tests for endpoint:
 - /tickets/<pk>/pay/
"""
import datetime

from django.urls import reverse
from rest_framework import status

from booking.models import Ticket
from booking.tests.test_url_tickets import TicketsBaseTestCase


class PayTicketPositiveTestCase(TicketsBaseTestCase):
    """
    Positive test case for ticket payment: /tickets/<int:pk>/pay/
    """

    def test_url_tickets_pay_positive_patch_user(self) -> None:
        """
        Positive test for user's PATCH request to /tickets/<int:pk>/pay/
        """
        response = self.client.patch(path=reverse('pay', args=[self.ticket.pk]),
                                     HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data['receipt'], '')

    def test_url_tickets_pay_positive_patch_admin(self) -> None:
        """
        Positive test for user's PATCH request to /tickets/<int:pk>/pay/
        """
        ticket = Ticket(showing=self.showing,
                        date_time=self.showing.date_time - datetime.timedelta(days=2),
                        row_number=3, seat_number=3, user=self.admin)
        ticket.save()
        response = self.client.patch(path=reverse('pay', args=[ticket.pk]),
                                     HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data['receipt'], '')

    def test_url_tickets_pay_positive_put_user(self) -> None:
        """
        Positive test for user's PUT request to /tickets/<int:pk>/pay/
        """
        response = self.client.put(path=reverse('pay', args=[self.ticket.pk]),
                                   HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data['receipt'], '')

    def test_url_tickets_pay_positive_put_admin(self) -> None:
        """
        Positive test for user's PUT request to /tickets/<int:pk>/pay/
        """
        ticket = Ticket(showing=self.showing,
                        date_time=self.showing.date_time - datetime.timedelta(days=2),
                        row_number=3, seat_number=3, user=self.admin)
        ticket.save()
        response = self.client.put(path=reverse('pay', args=[ticket.pk]),
                                   HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data['receipt'], '')

    def test_url_tickets_pay_positive_admin_pays_for_user(self) -> None:
        """
        Negative test checks that admin can't pay for someone's else ticket
        """
        response = self.client.put(path=reverse('pay', args=[self.ticket.pk]),
                                   HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data['receipt'], '')


class PayTicketNegativeTestCase(TicketsBaseTestCase):
    """
    Negative test case for ticket payment: /tickets/<int:pk>/pay/
    """

    def test_url_tickets_pay_negative_unsupported_methods(self) -> None:
        """
        Negative test checks that GET, POST, DELETE requests not supported
        """
        admin_ticket = Ticket(user=self.admin,
                              showing=self.showing,
                              row_number=3, seat_number=3,
                              date_time=self.showing.date_time - datetime.timedelta(days=2))
        admin_ticket.save()
        tokens = [self.user_token, self.admin_token]
        tickets = [self.ticket, admin_ticket]
        for ticket, token in zip(tickets, tokens):
            response = self.client.get(path=reverse('pay', args=[ticket.pk]),
                                       content_type='application/json',
                                       HTTP_AUTHORIZATION=f'Bearer {token}')
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

            response = self.client.post(path=reverse('pay', args=[ticket.pk]),
                                        content_type='application/json',
                                        HTTP_AUTHORIZATION=f'Bearer {token}')
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

            response = self.client.delete(path=reverse('pay', args=[ticket.pk]),
                                          content_type='application/json',
                                          HTTP_AUTHORIZATION=f'Bearer {token}')
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_url_tickets_pay_negative_wrong_ticket_user(self) -> None:
        """
        Negative test checks that user can't pay for someone's else ticket
        """
        admin_ticket = Ticket(user=self.admin,
                              showing=self.showing,
                              row_number=3, seat_number=3,
                              date_time=self.showing.date_time - datetime.timedelta(days=2))
        admin_ticket.save()
        response = self.client.put(path=reverse('pay', args=[admin_ticket.pk]),
                                   HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_url_tickets_pay_negative_paid_ticket_user(self) -> None:
        """
        Negative test checks that user can't pay for paid ticket
        """
        self.ticket.receipt = 'receipt'
        self.ticket.save()
        response = self.client.put(path=reverse('pay', args=[self.ticket.pk]),
                                   content_type='application/json',
                                   HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_url_tickets_pay_negative_paid_ticket_admin(self) -> None:
        """
        Negative test checks that admin can't pay for paid ticket
        """
        admin_ticket = Ticket(user=self.admin,
                              receipt='ok',
                              showing=self.showing,
                              row_number=3, seat_number=3,
                              date_time=self.showing.date_time - datetime.timedelta(days=2))
        admin_ticket.save()
        response = self.client.put(path=reverse('pay', args=[admin_ticket.pk]),
                                   HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
