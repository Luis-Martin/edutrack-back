from api import models, serializers
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


# PROFESSOR

# Registro de nuevo profesor.
# 1. Recibe datos, fuerza username=email.
# 2. Valida y crea profesor.
# 3. Guarda contraseña hasheada.
# 4. Devuelve datos del profesor.
@api_view(['POST'])
def professor_register(request):
    serializer = serializers.ProfessorSerializer(data={**request.data, 'username': request.data['email']})
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    professor = serializer.create(serializer.validated_data)
    professor.set_password(request.data['password'])
    professor.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)

# Login de profesores.
# 1. Recibe email y contraseña.
# 2. Busca profesor y valida contraseña.
# 3. Devuelve token y datos del profesor.
@api_view(['POST'])
def professor_login(request):
    professor = get_object_or_404(models.Professor, email=request.data['email'])
    if not professor.check_password(request.data['password']):
        return Response({"error": "Invalid username or password"}, status=status.HTTP_400_BAD_REQUEST)
    token, created = Token.objects.get_or_create(user=professor)
    serializer = serializers.ProfessorSerializer(instance=professor)
    return Response({"token": token.key, "professor": serializer.data}, status=status.HTTP_200_OK)

# Perfil del profesor autenticado.
# 1. Requiere autenticación.
# 2. Devuelve datos del profesor.
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def professor_profile(request):
    professor = get_object_or_404(models.Professor, email=request.data['email'])
    serializer = serializers.ProfessorSerializer(instance=professor)
    return Response(serializer.data, status=status.HTTP_200_OK)


# STUDENT

# Registro de nuevo estudiante.
# 1. Recibe datos, fuerza username=email.
# 2. Valida y crea estudiante.
# 3. Guarda contraseña hasheada.
# 4. Devuelve datos del estudiante.
@api_view(['POST'])
def student_register(request):
    serializer = serializers.StudentSerializer(data={**request.data, 'username': request.data['email']})
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    student = serializer.create(serializer.validated_data)
    student.set_password(request.data['password'])
    student.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)

# Login de estudiantes.
# 1. Recibe email y contraseña.
# 2. Busca estudiante y valida contraseña.
# 3. Devuelve token y datos del estudiante.
@api_view(['POST'])
def student_login(request):
    student = get_object_or_404(models.Student, email=request.data['email'])
    if not student.check_password(request.data['password']):
        return Response({"error": "Invalid username or password"}, status=status.HTTP_400_BAD_REQUEST)
    token, created = Token.objects.get_or_create(user=student)
    serializer = serializers.StudentSerializer(instance=student)
    return Response({"token": token.key, "student": serializer.data}, status=status.HTTP_200_OK)

# Perfil del estudiante autenticado.
# 1. Requiere autenticación.
# 2. Devuelve datos del estudiante.
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def student_profile(request):
    student = get_object_or_404(models.Student, email=request.data['email'])
    serializer = serializers.StudentSerializer(instance=student)
    return Response(serializer.data, status=status.HTTP_200_OK)


# COURSE

# Listado de cursos.
# 1. Requiere autenticación.
# 2. Devuelve todos los cursos solo si el usuario autenticado es un profesor.
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


# OPEN COURSE

# Crear curso con sus horarios o listar cursos aperturados del profesor autenticado.
# POST: Crea un curso aperturado con sus horarios.
# GET: Lista todos los cursos aperturados del profesor autenticado.
@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def opencourse(request):
    user = request.user
    # Verifica que el usuario autenticado sea un profesor
    if not hasattr(user, 'professor'):
        return Response({"error": "Solo los profesores pueden acceder a este recurso."}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'POST':
        try:
            # Obtener el profesor autenticado
            professor = get_object_or_404(models.Professor, email=user.email)

            # Validar que los datos requeridos estén presentes
            if 'open_course' not in request.data:
                return Response({"error": "Se requiere el campo 'open_course'"}, status=status.HTTP_400_BAD_REQUEST)
            
            if 'schedule' not in request.data:
                return Response({"error": "Se requiere el campo 'schedule'"}, status=status.HTTP_400_BAD_REQUEST)

            # Crear Curso Aperturado
            open_course_data = request.data['open_course'].copy()
            open_course_data['id_professor'] = professor.id_professor

            # Validar que el curso existe
            if 'id_course' not in open_course_data:
                return Response({"error": "Se requiere el campo 'id_course'"}, status=status.HTTP_400_BAD_REQUEST)
            
            course = get_object_or_404(models.Course, id_course=open_course_data['id_course'])

            open_course_serializer = serializers.OpenCourseSerializer(data=open_course_data)
            if not open_course_serializer.is_valid():
                return Response(open_course_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            # Guardar el curso aperturado
            open_course_instance = open_course_serializer.save()
            
            # Crear los horarios
            schedule_data = request.data['schedule']
            created_schedules = []

            for schedule_item in schedule_data:
                # Asignar el id_open_course al horario
                schedule_item['id_open_course'] = open_course_instance.id_open_course
                
                schedule_serializer = serializers.ScheduleSerializer(data=schedule_item)
                if not schedule_serializer.is_valid():
                    # Si hay error en algún horario, eliminar el curso aperturado creado
                    open_course_instance.delete()
                    return Response(schedule_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
                # Guardar el horario
                schedule_instance = schedule_serializer.save()
                created_schedules.append(schedule_instance)
            
            # Obtener todos los horarios del curso aperturado desde la base de datos
            schedules_from_db = models.Schedule.objects.filter(id_open_course=open_course_instance.id_open_course)
            all_schedules_serializer = serializers.ScheduleSerializer(instance=schedules_from_db, many=True)

            # Construir la respuesta con "schedule" como campo de "open_course"
            open_course_response = open_course_serializer.data.copy()
            open_course_response["schedule"] = all_schedules_serializer.data

            return Response(open_course_response, status=status.HTTP_201_CREATED)
            
        except models.Course.DoesNotExist:
            return Response({"error": "El curso especificado no existe"}, status=status.HTTP_404_NOT_FOUND)
        except models.Professor.DoesNotExist:
            return Response({"error": "Profesor no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Error interno del servidor: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    elif request.method == 'GET':
        try:
            professor = get_object_or_404(models.Professor, email=user.email)
            # Obtener todos los cursos aperturados de este profesor
            open_courses = models.OpenCourse.objects.filter(id_professor=professor.id_professor)
        
            response_data = []
            for open_course in open_courses:
                open_course_serializer = serializers.OpenCourseSerializer(instance=open_course)
                # Obtener los horarios asociados a este curso aperturado
                schedules = models.Schedule.objects.filter(id_open_course=open_course.id_open_course)
                schedule_serializer = serializers.ScheduleSerializer(instance=schedules, many=True)
                # Construir la respuesta para este curso aperturado
                open_course_data = open_course_serializer.data.copy()
                open_course_data["schedule"] = schedule_serializer.data
                response_data.append(open_course_data)
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": f"Error interno del servidor: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

