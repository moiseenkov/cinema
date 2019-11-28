import logging
import time

from celery import shared_task

from booking.models import Ticket


logger = logging.getLogger(__name__)


@shared_task
def pay_ticket(*args, **kwargs):
    time.sleep(15)
    pk = kwargs.get('pk', None)
    payment_uuid = kwargs.get('payment_uuid', None)

    if not (pk and payment_uuid):
        logger.warning(f'Incorrect payment arguments were given: {kwargs}')
        return

    ticket = Ticket.objects.filter(pk=pk).first()
    if ticket is None:
        logger.warning(f'Ticket with id {pk} was not found')
        return

    ticket.receipt = payment_uuid
    ticket.save()
