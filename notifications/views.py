import logging
from typing import Any

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from notifications.models import DeliveryLog, Message
from notifications.serializers import NotifySerializer

from .tasks import schedule_email_notifications, schedule_telegram_notifications
from .utils import is_valid_email, is_valid_telegram_id

logger = logging.getLogger(__name__)


class NotifyView(APIView):
    """
        API view to handle notification requests.

        This view accepts POST requests with details of the notification to be sent.
        It validates the request data, stores it in the database, and schedules the
        delivery of the notification using Celery tasks.
        """

    def post(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        """
        Handles POST requests to create and schedule notifications.

        Args:
            request: The HTTP request object containing notification details.

        Returns:
            Response: A DRF Response object with the outcome of the request.
        """
        serializer = NotifySerializer(data=request.data)

        # Validate incoming data
        if not serializer.is_valid():
            logger.warning("Invalid notification data: %s", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Extract validated data
        subject = serializer.validated_data.get("subject", "No Subject")
        message = serializer.validated_data["message"]
        recipient = serializer.validated_data["recipient"]
        delay = serializer.validated_data["delay"]

        # Save notification to the database
        try:
            notification = Message.objects.create(
                subject=subject,
                message=message,
                recipient=recipient,
                delay=delay
            )
        except Exception as e:
            logger.error("Failed to save notification: %s", str(e))
            return Response(
                {"error": f"Failed to save notification: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        # Categorize recipients
        emails = [r for r in recipient if is_valid_email(r)]
        telegram_ids = [r for r in recipient if is_valid_telegram_id(r)]

        # Schedule notifications via Celery tasks
        try:
            if not emails and not telegram_ids:
                logger.warning("No valid recipients to send notifications.")
                DeliveryLog.objects.create(
                    message_id=notification.id,
                    status='failed',
                    error_message="No valid recipients to send notifications."
                )
                return Response(
                    {"No valid recipients to send notifications."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                # Email notifications
                if emails:
                    logger.info("Scheduling email notifications for: %s", emails)
                    schedule_email_notifications(emails, subject, message, delay)
                    # Telegram notifications
                if telegram_ids:
                    logger.info("Scheduling Telegram notifications for: %s", telegram_ids)
                    schedule_telegram_notifications(telegram_ids, message, delay)

                # Log successful scheduling
                DeliveryLog.objects.create(
                    message_id=notification.id,
                    status='sent',
                    error_message=''
                )
                return Response(
                    {"message": "Notification has been scheduled."},
                    status=status.HTTP_202_ACCEPTED,
                )

        except Exception as e:
            logger.error("Failed to schedule notification: %s", str(e))
            DeliveryLog.objects.create(
                message_id=notification.id,
                status='failed',
                error_message=str(e)
            )

            return Response(
                {"error": f"Failed to schedule notification: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
