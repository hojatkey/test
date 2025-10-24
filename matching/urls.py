from django.urls import path
from . import views

app_name = "matching"

urlpatterns = [
    path("", views.matching_algorithm, name="algorithm"),
    path("matches/", views.matches, name="matches"),
    path("matches/<int:match_id>/", views.match_detail, name="match_detail"),
    path("matches/<int:match_id>/accept/", views.accept_match, name="accept_match"),
    path("matches/<int:match_id>/reject/", views.reject_match, name="reject_match"),
    path("select-candidate/<int:candidate_id>/", views.select_candidate, name="select_candidate"),
]
