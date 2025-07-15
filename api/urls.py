from django.urls import path
from api.views.professor import professor_register, professor_login, professor_profile
from api.views.student import student_register, student_login, student_profile, professor_students
from api.views.course import courses
from api.views.opencourse import professor_opencourse
from api.views.enrollstudent import professor_enrollstudent, student_enrollstudent, professor_deleteenrollstudent
from api.views.attendance import professor_attendance, student_attendance
from api.views.notes import professor_note, student_note

urlpatterns = [
    # Professor
    path('professor/register', professor_register),
    path('professor/login', professor_login),
    path('professor/profile', professor_profile),
    path('professor/opencourse', professor_opencourse),
    path('professor/enrollstudent', professor_enrollstudent),
    path('professor/deleteenrollstudent', professor_deleteenrollstudent),
    path('professor/attendance', professor_attendance),
    path('professor/note', professor_note),
    path('professor/students', professor_students),
    # Student
    path('student/register', student_register),
    path('student/login', student_login),
    path('student/profile', student_profile),
    path('student/enrollstudent', student_enrollstudent),
    path('student/attendance', student_attendance),
    path('student/note', student_note),
    # Course
    path('courses', courses),
]