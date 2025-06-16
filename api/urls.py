from django.urls import path, re_path
from api import views

urlpatterns = [
    re_path('professor/login', views.professor_login),
    re_path('professor/register', views.professor_register),
    re_path('professor/profile', views.professor_profile),
]