from typing import Any

from rest_framework import serializers


class NotifySerializer(serializers.Serializer):
    """
    Serializer for processing notification data.

    Attributes:
        subject (CharField): The subject of the notification. Defaults to "No Subject".
        message (CharField): The content of the notification message.
        recipient (JSONField): A list or single recipient of the notification.
                               Accepts a JSON object that may contain a string or list of strings.
        delay (ChoiceField): The delay for sending the notification.
                             Options are:
                             - 0: Instant
                             - 1: 1 Hour
                             - 2: 1 Day
    """
    subject = serializers.CharField(max_length=255, default="No Subject")
    message = serializers.CharField(max_length=1024)
    recipient = serializers.JSONField()
    delay = serializers.ChoiceField(choices=[(0, 'Instant'), (1, '1 Hour'), (2, '1 Day')])

    def to_internal_value(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Convert input data to internal value (list) if 'recipient' is a string.
        """
        recipients = data.get('recipient', None)

        if isinstance(recipients, str):
            data['recipient'] = [recipients]

        return super().to_internal_value(data)

    def validate_recipients(self, value: list[str] | str) -> list:
        """
        Validate the recipients field to ensure it contains valid data.

        - If the value is not a list, convert it to a list containing a single element.
        - Validate that each recipient in the list is a string with a maximum length of 150 characters.

        Args:
            value: The input data for the recipient field.

        Returns:
            list: A validated list of recipients.

        Raises:
            serializers.ValidationError: If any recipient is invalid.
        """
        if not isinstance(value, list):
            value = [value]

        for recipient in value:
            if not isinstance(recipient, str) or len(recipient) > 150:
                raise serializers.ValidationError(f"Invalid recipient: {recipient}")

        return value
