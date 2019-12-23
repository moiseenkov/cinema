"""
Booking app Celery tasks module
"""
import datetime
import logging
import time

import pytz
from celery import shared_task

from booking.models import Ticket, Showing


@shared_task
def pay_ticket(**kwargs):
    """
    Celery task processes ticket payment: waits 15 sec and saves receipt in ticket
    """
    logger = logging.getLogger(__name__)
    time.sleep(15)
    pkey = kwargs.get('pk', None)
    payment_uuid = kwargs.get('payment_uuid', None)

    if not (pkey and payment_uuid):
        logger.warning('Incorrect payment arguments were given: %s', kwargs)
        return

    ticket = Ticket.objects.filter(pk=pkey).first()
    if ticket is None:
        logger.warning('Ticket with id %s was not found', pkey)
        return

    ticket.receipt = payment_uuid
    ticket.save()


@shared_task(bind=True)
def disable_bookings():
    """
    Celery task that disables bookings for showings that are coming up in 2 hours
    """
    deadline = datetime.datetime.now(tz=pytz.utc) + datetime.timedelta(hours=2)
    showing_ids = [showing.pk for showing in Showing.objects.filter(date_time__lte=deadline)]
    Ticket.objects.filter(showing__in=showing_ids, receipt='').delete()
