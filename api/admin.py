from django.contrib import admin
from api import models

@admin.register(models.Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('id_professor', 'username', 'first_name', 'last_name', 'email', 'phone', 'created_at', 'updated_at', 'password')
    search_fields = ('id_professor', 'first_name', 'last_name', 'email')
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
    list_display = ('id_open_course', 'id_professor', 'id_course', 'start_class', 'end_class', 'academic_year', 'academic_semester', 'professional_career', 'section')
    search_fields = ('id_professor__first_name','id_professor__last_name', 'id_professor__email', 'academic_year')
    list_filter = ('created_at','updated_at')

@admin.register(models.Schedule)
class OpenCourseAdmin(admin.ModelAdmin):
    list_display = ('id_schedule', 'id_open_course', 'day_week', 'start_hour', 'end_hour')
    search_fields = ('id_open_course__id_professor__first_name','id_open_course__id_professor__last_name', 'id_open_course__id_professor__email',
                     'id_open_course__academic_year', 'day_week')
    list_filter = ('created_at','updated_at')

@admin.register(models.EnrollStudent)
class EnrollStudentAdmin(admin.ModelAdmin):
    list_display = ('id_enroll_student', 'id_student', 'id_open_course')
    search_fields = ('id_student__first_name','id_student__last_name', 'id_student__email',
                     'id_open_course__id_professor__first_name','id_open_course__id_professor__last_name', 'id_open_course__id_professor__email',
                     'id_open_course__academic_year')
    list_filter = ('created_at','updated_at')

@admin.register(models.Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('id_attendance', 'id_enroll_student', 'date', 'attendance')
    search_fields = ('id_enroll_student__id_student__first_name','id_enroll_student__id_student__last_name', 'id_enroll_student__id_student__email',
                     'id_enroll_student__id_open_course__id_professor__first_name','id_enroll_student__id_open_course__id_professor__last_name', 'id_enroll_student__id_open_course__id_professor__email',
                     'id_enroll_student__id_open_course__academic_year')
    list_filter = ('created_at','updated_at')


@admin.register(models.Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('id_note', 'id_enroll_student', 'type_note', 'note', 'created_at', 'updated_at')
    search_fields = ('id_enroll_student__id_student__first_name', 'id_enroll_student__id_student__last_name', 'id_enroll_student__id_student__email', 'type_note')
    list_filter = ('type_note', 'created_at', 'updated_at')
