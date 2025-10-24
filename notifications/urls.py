from django.urls import path
from . import views

app_name = "notifications"

urlpatterns = [
    path("", views.notifications, name="notifications"),
    path("<int:notification_id>/read/", views.mark_as_read, name="mark_as_read"),
    path("messages/", views.messages_list, name="messages"),
    path("messages/send/", views.send_message, name="send_message"),
    path("messages/<int:message_id>/", views.message_detail, name="message_detail"),
]
