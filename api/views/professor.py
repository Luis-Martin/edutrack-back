from api import models, serializers
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


# Vista para registrar un nuevo profesor
@api_view(['POST'])
def professor_register(request):
    # Serializa los datos recibidos y agrega el username igual al email
    serializer = serializers.ProfessorSerializer(data={**request.data, 'username': request.data['email']})
    
    # Valida los datos del profesor
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Crea y guarda el nuevo profesor
    professor = serializer.create(serializer.validated_data)
    professor.set_password(request.data['password'])
    professor.save()
    
    # Retorna los datos del profesor creado
    return Response(serializer.data, status=status.HTTP_201_CREATED)


# Vista para login de profesor
@api_view(['POST'])
def professor_login(request):
    # Busca al profesor por email
    professor = get_object_or_404(models.Professor, email=request.data['email'])
    
    # Verifica la contraseña
    if not professor.check_password(request.data['password']):
        return Response({"error": "Invalid username or password"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Obtiene o crea el token de autenticación
    token, created = Token.objects.get_or_create(user=professor)
    serializer = serializers.ProfessorSerializer(instance=professor)
    
    # Retorna el token y los datos del profesor
    return Response({"token": token.key, "professor": serializer.data}, status=status.HTTP_200_OK)


# Vista para obtener el perfil del profesor autenticado
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def professor_profile(request):
    user = request.user
    # Busca al profesor por email
    professor = get_object_or_404(models.Professor, email=user)
    serializer = serializers.ProfessorSerializer(instance=professor)
    
    # Retorna los datos del profesor
    return Response(serializer.data, status=status.HTTP_200_OK) 