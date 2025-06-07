from students.models import Student
from rest_framework import viewsets, permissions
from students.serializers import StudentSerilizer

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = StudentSerilizer
