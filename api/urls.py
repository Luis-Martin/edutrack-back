from django.urls import path
from api.views.professor import professor_register, professor_login, professor_profile
from api.views.student import student_register, student_login, student_profile
from api.views.course import courses
from api.views.opencourse import professor_opencourse
from api.views.enrollstudent import professor_enrollstudent

urlpatterns = [
    # Professor
    path('professor/register', professor_register),
    path('professor/login', professor_login),
    path('professor/profile', professor_profile),
    path('professor/opencourse', professor_opencourse),
    path('professor/enrollstudent', professor_enrollstudent),
    # Student
    path('student/register', student_register),
    path('student/login', student_login),
    path('student/profile', student_profile),
    # Course
    path('courses', courses),
]