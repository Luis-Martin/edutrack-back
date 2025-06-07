from professor.models import Professor
from rest_framework import viewsets, permissions
from professor.serializers import ProfessorSerilizer

class ProfessorViewSet(viewsets.ModelViewSet):
    queryset = Professor.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = ProfessorSerilizer
