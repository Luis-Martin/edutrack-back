from api import models, serializers
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@api_view(['POST'])
def student_register(request):
    serializer = serializers.StudentSerializer(data={**request.data, 'username': request.data['email']})
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    student = serializer.create(serializer.validated_data)
    student.set_password(request.data['password'])
    student.save()
    
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def student_login(request):
    student = get_object_or_404(models.Student, email=request.data['email'])
    
    if not student.check_password(request.data['password']):
        return Response({"error": "Invalid username or password"}, status=status.HTTP_400_BAD_REQUEST)
    
    token, created = Token.objects.get_or_create(user=student)
    serializer = serializers.StudentSerializer(instance=student)
    
    return Response({"token": token.key, "student": serializer.data}, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def student_profile(request):
    student = get_object_or_404(models.Student, email=request.data['email'])
    serializer = serializers.StudentSerializer(instance=student)
    
    return Response(serializer.data, status=status.HTTP_200_OK) 