from api import models, serializers
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


# Vista para registrar un nuevo estudiante
@api_view(['POST'])
def student_register(request):
    # Serializa los datos recibidos y agrega el username igual al email
    serializer = serializers.StudentSerializer(data={**request.data, 'username': request.data['email']})
    
    # Valida los datos del estudiante
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Crea y guarda el nuevo estudiante
    student = serializer.create(serializer.validated_data)
    student.set_password(request.data['password'])
    student.save()
    
    # Retorna los datos del estudiante creado
    return Response(serializer.data, status=status.HTTP_201_CREATED)


# Vista para login de estudiante
@api_view(['POST'])
def student_login(request):
    # Busca al estudiante por email
    student = get_object_or_404(models.Student, email=request.data['email'])
    
    # Verifica la contraseña
    if not student.check_password(request.data['password']):
        return Response({"error": "Invalid username or password"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Obtiene o crea el token de autenticación
    token, created = Token.objects.get_or_create(user=student)
    serializer = serializers.StudentSerializer(instance=student)
    
    # Retorna el token y los datos del estudiante
    return Response({"token": token.key, "student": serializer.data}, status=status.HTTP_200_OK)


# Vista para obtener o actualizar el perfil del estudiante autenticado
@api_view(['GET', 'PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def student_profile(request):
    # Obtiene el estudiante autenticado por el usuario del request
    student = get_object_or_404(models.Student, email=request.user.email)

    if request.method == 'GET':
        serializer = serializers.StudentSerializer(instance=student)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        data = request.data.copy()
        
        # Solo permitir actualizar ciertos campos
        allowed_fields = ['first_name', 'last_name', 'email', 'phone', 'password']
        
        for field in allowed_fields:
            if field in data:
                if field == 'password':
                    student.set_password(data['password'])
                else:
                    setattr(student, field, data[field])
        student.save()

        serializer = serializers.StudentSerializer(instance=student)
        return Response(serializer.data, status=status.HTTP_200_OK)