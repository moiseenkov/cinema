import datetime
import logging
import time

import pytz
from celery import shared_task

from booking.models import Ticket, Showing

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


@shared_task(bind=True)
def disable_bookings(*args, **kwargs):
    deadline = datetime.datetime.now(tz=pytz.utc) + datetime.timedelta(hours=2)
    showing_ids = [showing.pk for showing in Showing.objects.filter(date_time__lte=deadline)]
    Ticket.objects.filter(showing__in=showing_ids, receipt='').delete()
