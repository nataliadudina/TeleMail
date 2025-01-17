from django.db import models


class Message(models.Model):
    subject = models.CharField(max_length=255, default="No Subject")
    message = models.TextField(max_length=1024)
    recipient = models.JSONField()
    delay = models.IntegerField(default=0, choices=((0, 'Instant'), (1, '1 Hour'), (2, '1 Day')))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message to {self.recipient}."


class DeliveryLog(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='logs')
    status = models.CharField(max_length=20, choices=(
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ))
    timestamp = models.DateTimeField(auto_now_add=True)
    error_message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Log for Message {self.message.id} - {self.status}"
