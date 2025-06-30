from api import models
from rest_framework import serializers

class ProfessorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Professor
        fields = [
            'id_professor',
            'username',
            'first_name',
            'last_name',
            'email',
            'phone',
            'created_at',
            'updated_at',
        ]

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Student
        fields = [
            'id_student',
            'username',
            'first_name',
            'last_name',
            'email',
            'phone',
            'created_at',
            'updated_at',
        ]

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Course
        fields = [
            'id_course',
            'name',
            'study_cycle',
            'credits',
            'duration_weeks',
            'theory_hours',
            'practice_hours',
            'study_plan',
            'subject_code',
        ]

class OpenCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OpenCourse
        fields = [
            'id_open_course',
            'id_professor',
            'id_course',
            'start_class',
            'end_class',
            'academic_year',
            'academic_semester',
            'professional_career',
            'section',
            'created_at',
            'updated_at',
        ]

class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Schedule
        fields = [
            'id_schedule',
            'id_open_course',
            'day_week',
            'start_hour',
            'end_hour',
            'created_at',
            'updated_at',
        ]