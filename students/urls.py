from django.urls import path
from . import views

app_name = "students"

urlpatterns = [
    path("profile/", views.student_profile, name="profile"),
    path("requests/", views.student_requests, name="requests"),
    path("requests/create/", views.create_request, name="create_request"),
    path("requests/<int:request_id>/edit/", views.edit_request, name="edit_request"),
    path("tests/", views.personality_tests, name="tests"),
    path("tests/<int:test_id>/take/", views.take_test, name="take_test"),
    path("files/", views.student_files, name="files"),
    path("files/upload/", views.upload_file, name="upload_file"),
    path("verification/", views.student_verification, name="verification"),
]
