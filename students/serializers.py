from rest_framework import serializers
from students.models import Student

class StudentSerilizer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ('id_student',
                  'first_name',
                  'last_name',
                  'email',
                  'phone',
                  'password',
                  'created_at',
                  'updated_at')
        read_only_fields = ('created_at',)
