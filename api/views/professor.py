from api import models, serializers
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['POST'])
def professor_register(request):
    serializer = serializers.ProfessorSerializer(data={**request.data, 'username': request.data['email']})
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    professor = serializer.create(serializer.validated_data)
    professor.set_password(request.data['password'])
    professor.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def professor_login(request):
    professor = get_object_or_404(models.Professor, email=request.data['email'])
    if not professor.check_password(request.data['password']):
        return Response({"error": "Invalid username or password"}, status=status.HTTP_400_BAD_REQUEST)
    token, created = Token.objects.get_or_create(user=professor)
    serializer = serializers.ProfessorSerializer(instance=professor)
    return Response({"token": token.key, "professor": serializer.data}, status=status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def professor_profile(request):
    user = request.user
    professor = get_object_or_404(models.Professor, email=user)
    serializer = serializers.ProfessorSerializer(instance=professor)
    return Response(serializer.data, status=status.HTTP_200_OK) 