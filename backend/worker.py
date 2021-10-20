import asyncio

from helper.config import config
from helper.email_helper import send_mail

from celery import Celery

celery = Celery(__name__)
celery.conf.broker_url = config['CELERY_BROKER_URL']

@celery.task(name="send_email_task")
def send_email_task(data):
    asyncio.get_event_loop().run_until_complete(send_mail(data))

