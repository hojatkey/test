from django.urls import path
from . import views

app_name = "notifications"

urlpatterns = [
    path("", views.notifications, name="notifications"),
    path("<int:notification_id>/read/", views.mark_as_read, name="mark_as_read"),
    path("messages/", views.messages_list, name="messages"),
    path("messages/send/", views.send_message, name="send_message"),
    path("messages/<int:message_id>/", views.message_detail, name="message_detail"),
    
    # API endpoints
    path("mark-read/<int:notification_id>/", views.mark_notification_read_api, name="mark_read_api"),
    path("mark-all-read/", views.mark_all_read_api, name="mark_all_read_api"),
    path("delete/<int:notification_id>/", views.delete_notification_api, name="delete_notification_api"),
    path("unread-count/", views.unread_count_api, name="unread_count_api"),
    path("stream/", views.notification_stream, name="notification_stream"),
]
