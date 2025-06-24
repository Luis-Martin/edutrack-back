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
