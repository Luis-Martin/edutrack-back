from django.urls import path, re_path
from api import views

urlpatterns = [
    re_path('professor/login', views.login),
    re_path('professor/register', views.register),
    re_path('professor/profile', views.profile),
]