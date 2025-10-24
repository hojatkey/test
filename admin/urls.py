from django.urls import path
from . import views

app_name = "admin"

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('verification/', views.verification_management, name='verification'),
    path('verification/<int:profile_id>/approve/', views.approve_verification, name='approve_verification'),
    path('verification/<int:profile_id>/reject/', views.reject_verification, name='reject_verification'),
    path('verification/<int:profile_id>/details/', views.verification_details, name='verification_details'),
]
