from api import models, serializers
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def courses(request):
    user = request.user
    
    # Verifica que el usuario autenticado sea un profesor
    if not hasattr(user, 'professor'):
        return Response({"error": "Solo los profesores pueden acceder a este recurso."}, status=status.HTTP_403_FORBIDDEN)
    
    courses = models.Course.objects.all()
    serializer = serializers.CourseSerializer(instance=courses, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK) 