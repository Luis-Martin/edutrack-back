from api import models, serializers
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


# Vista para obtener la lista de cursos
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def courses(request):
    user = request.user
    
    # Obtiene todos los cursos de la base de datos
    courses = models.Course.objects.all()
    # Serializa la lista de cursos
    serializer = serializers.CourseSerializer(instance=courses, many=True)
    
    # Retorna la lista de cursos serializados
    return Response(serializer.data, status=status.HTTP_200_OK) 