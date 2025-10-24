from django.urls import path
from . import views

app_name = "companies"

urlpatterns = [
    path("profile/", views.company_profile, name="profile"),
    path("requests/", views.job_requests, name="requests"),
    path("requests/create/", views.create_job_request, name="create_job_request"),
    path("requests/<int:request_id>/edit/", views.edit_job_request, name="edit_job_request"),
    path("matching/", views.matching, name="matching"),
    path("candidates/", views.candidates, name="candidates"),
    path("candidates/<int:student_id>/", views.candidate_detail, name="candidate_detail"),
]
