import time

from celery import shared_task


@shared_task
def pay_ticket(*args, **kwargs):
    time.sleep(15)
