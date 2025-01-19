from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Message, DeliveryLog


class NotifyViewTests(APITestCase):
    def setUp(self):
        """
        Initialize data before each test.
        """
        self.valid_payload = {
            "subject": "Test Notification",
            "message": "This is a test message.",
            "recipient": ["test@example.com", "123456789"],
            "delay": 1,
        }
        self.invalid_payload = {
            "subject": "Test Notification",
            "message": "This is a test message.",
            "recipient": "invalid_email",
            "delay": 1,
        }
        self.url = reverse("notifications:notify")

    def test_create_notification_success(self):
        """
        Test for successful notification creation.
        """
        response = self.client.post(self.url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertIn("message", response.data)
        self.assertEqual(Message.objects.count(), 1)

        # Check the created notification
        message = Message.objects.first()
        self.assertEqual(message.subject, self.valid_payload["subject"])
        self.assertEqual(message.message, self.valid_payload["message"])
        self.assertEqual(message.recipient, self.valid_payload["recipient"])

    def test_create_notification_invalid_recipient(self):
        """
        Test for creating a notification with an invalid recipient.
        """
        response = self.client.post(self.url, self.invalid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("No valid recipients to send notifications.", response.data)
        self.assertEqual(Message.objects.count(), 0)

    def test_create_notification_no_recipients(self):
        """
        Test for when the recipient list is empty.
        """
        payload = {
            "subject": "Test Notification",
            "message": "This is a test message.",
            "recipient": [],
            "delay": 1,
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("No valid recipients to send notifications.", response.data)
        self.assertEqual(Message.objects.count(), 0)

        # Check delivery log
        log = DeliveryLog.objects.first()
        self.assertEqual(log.status, "failed")
        self.assertIn("No valid recipients", log.error_message)

    def test_create_notification_missing_fields(self):
        """
        Test for when required fields are missing.
        """
        payload = {
            "message": "This is a test message.",
            "recipient": ["test@example.com"],
            # 'delay' field is missing
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("delay", response.data)

    def test_create_notification_partial_success(self):
        """
        Test for when some recipients are valid, and some are not.
        """
        payload = {
            "subject": "Test Notification",
            "message": "This is a test message.",
            "recipient": ["valid@example.com", "invalid_email"],  # Mixed recipients
            "delay": 1,
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertIn("message", response.data)

        # Ensure that the message is saved
        self.assertEqual(Message.objects.count(), 1)
        message = Message.objects.first()

        # Ensure that only valid recipients are saved
        valid_recipients = ["valid@example.com"]
        self.assertListEqual(message.recipient, valid_recipients)

