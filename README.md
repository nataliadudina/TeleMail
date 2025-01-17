# Notification Service TeleMail

A comprehensive notification service for sending email and Telegram notifications based on scheduled delays. This service is designed to handle both instant and delayed notifications to multiple recipients. It supports both email and Telegram messages, offering a flexible system for notification management.

## Features

- **Email Notifications**: Send email messages to one or multiple recipients.
- **Telegram Notifications**: Send messages to Telegram users using the Telegram Bot API.
- **Scheduling**: Schedule notifications with a delay (1 hour, 1 day).
- **Flexible Recipient Handling**: Supports single or multiple recipients in the form of email addresses or Telegram IDs.
- **Error Handling**: Logs and handles errors during notification dispatching.

## Tech Stack

- **Backend Framework**: Django
- **Task Queue**: Celery with Redis as the broker
- **Database**: PostgreSQL
- **Message Queue**: Redis
- **Email**: Django's built-in `send_mail` function
- **Telegram API**: Telegram Bot API

## Requirements

Before running the project, ensure you have the following dependencies installed:

- Python 3.11+
- Django 3.x+
- Celery
- Redis
- PostgreSQL
- Python packages from `pyproject.toml`

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/nataliadudina/TeleMail.git
   cd TeleMail

2. **Install dependencies:**
 Make sure you have a virtual environment activated, then install the required packages:
    ```bash
     poetry install
   ```

3. **Set up environment variables:** 

Create a .env file in the project root and add the variables from .env_sample

4. **Setup PostgreSQL database:**

   ```bash
     psql -U postgres
     CREATE DATABASE <db_name>;
   ```

5. **Apply database migrations:**

   ```bash
     python manage.py migrate
   ```

6. **Run Redis and Celery:** 

   ```bash
    sudo service redis-server start
    celery -A config worker --loglevel=info --pool=solo
   ```
7. **Run the Django development server:**

   ```bash
    python manage.py runserver
   ```

## Usage

1. **Create a Notification**
Send a POST request to the /api/notify/ endpoint with the following JSON data:

```bash
{
  "subject": "Notification Subject",
  "message": "This is the message content",
  "recipient": ["recipient@example.com", "123456789"],
  "delay": 1
}
```
- *subject*: Subject of the notification (optional).

- *message*: Message content to be sent.

- *recipient*: A list of recipients (email addresses or Telegram IDs) or a string (single mail addresses or Telegram ID).

- *delay*: Delay for scheduling the notification (0 for instant sending, 1 for 1 hour delay, 2 for 1 day delay).

2. **Check Notification Status**

The system logs the status of each started campaign in the DeliveryLog table.