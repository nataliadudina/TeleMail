from django.urls import path

from notifications.apps import NotificationsConfig
from notifications.views import NotifyView

app_name = NotificationsConfig.name

urlpatterns = [
    path("api/notify/", NotifyView.as_view(), name="notify"),
]
