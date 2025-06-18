from django.contrib import admin
from api import models

@admin.register(models.Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('id_professor', 'username', 'first_name', 'last_name', 'email', 'phone', 'created_at', 'updated_at', 'password')
    search_fields = ('id_student', 'first_name', 'last_name', 'email')
    list_filter = ('created_at','updated_at')

@admin.register(models.Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('id_student', 'username', 'first_name', 'last_name', 'email', 'phone', 'created_at', 'updated_at', 'password')
    search_fields = ('id_student', 'first_name', 'last_name', 'email')
    list_filter = ('created_at','updated_at')

@admin.register(models.Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id_course', 'name', 'study_cycle', 'credits', 'duration_weeks', 'theory_hours', 'practice_hours', 'study_plan', 'subject_code')
    search_fields = ('id_course', 'name', 'study_plan', 'subject_code')
    list_filter = ('created_at','updated_at')

@admin.register(models.OpenCourse)
class OpenCourseAdmin(admin.ModelAdmin):
    list_display = ('id_open_course', 'id_professor', 'start_class', 'end_class', 'academic_year', 'academic_semester', 'professional_career', 'section')
    search_fields = ('id_open_course', 'id_professor')
    list_filter = ('created_at','updated_at')

@admin.register(models.Schedule)
class OpenCourseAdmin(admin.ModelAdmin):
    list_display = ('id_schedule', 'id_open_course', 'day_week', 'start_hour', 'end_hour')
    search_fields = ('id_schedule', 'id_open_course')
    list_filter = ('created_at','updated_at')
