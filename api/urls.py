from api import views
from django.urls import path, re_path

urlpatterns = [
    # Professor
    re_path('professor/register', views.professor_register),
    re_path('professor/login', views.professor_login),
    re_path('professor/profile', views.professor_profile),
    # Student
    re_path('student/register', views.student_register),
    re_path('student/login', views.student_login),
    re_path('student/profile', views.student_profile),
    # Course
    re_path('courses', views.courses),
]