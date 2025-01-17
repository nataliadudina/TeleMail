import re


def is_valid_email(recipient: str) -> bool:
    """
    Check if the given recipient is a valid email address.

    Args:
        recipient (str): The recipient string to validate.

    Returns:
        bool: True if the recipient is a valid email, False otherwise.
    """
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, recipient) is not None


def is_valid_telegram_id(recipient: str) -> bool:
    """
    Check if the given recipient is a valid Telegram ID.

    Args:
        recipient (str): The recipient string to validate.

    Returns:
        bool: True if the recipient is a valid Telegram ID, False otherwise.
    """
    return recipient.isdigit()
