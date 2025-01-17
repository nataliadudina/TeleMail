import os
from datetime import timedelta

import requests
from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.mail import send_mail
from django.utils import timezone

from config import settings

logger = get_task_logger(__name__)


@shared_task
def send_telegram_message_task(chat_id: int, message: str, url: str, token: str) -> None:
    """Celery task for sending Telegram messages"""
    try:
        response = requests.post(url=f'{url}{token}/sendMessage?chat_id={chat_id}&text={message}')
        response.raise_for_status()
        logger.info(f"Telegram message sent to chat_id {chat_id}")

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send Telegram message to chat_id {chat_id}: {str(e)}")


def schedule_telegram_notifications(chat_ids: list[str], message: str, delay: int) -> None:
    """Schedule Telegram messaging"""
    URL = os.getenv('TELEGRAM_URL')
    TOKEN = os.getenv('TELEGRAM_API_TOKEN')

    eta = timezone.now()
    if delay == 1:
        eta += timedelta(hours=1)
    elif delay == 2:
        eta += timedelta(days=1)

    for chat_id in chat_ids:
        send_telegram_message_task.apply_async(
            args=(chat_id, message, URL, TOKEN),
            eta=eta
        )


@shared_task
def send_email_task(subject: str, message: str, recipient: list[str]) -> None:
    """Celery task for sending email notifications."""
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[recipient],
            fail_silently=False,
        )
        logger.info(f"Email sent successfully to {recipient}")

    except Exception as e:
        logger.error(f"Failed to send email to {recipient}: {str(e)}")


def schedule_email_notifications(emails: list[str], subject: str, message: str, delay: int) -> None:
    """Schedule email messaging"""
    eta = timezone.now()
    if delay == 1:
        eta += timedelta(hours=1)
    elif delay == 2:
        eta += timedelta(days=1)

    for email in emails:
        send_email_task.apply_async(
            args=[subject, message, email],
            eta=eta
        )
