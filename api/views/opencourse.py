from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from api import models, serializers


# Vista para que un profesor pueda crear (POST) o listar (GET) los cursos aperturados
@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def professor_opencourse(request):
    """
    Vista para que un profesor pueda crear (POST) o listar (GET) los cursos aperturados.
    Solo los usuarios autenticados que sean profesores pueden acceder.
    """
    user = request.user

    # Verifica que el usuario autenticado sea un profesor
    if not hasattr(user, 'professor'):
        return Response({"error": "Solo los profesores pueden acceder a este recurso."}, status=403)
    
    # Si la petición es POST, crea un nuevo curso aperturado
    if request.method == 'POST':
        return _create_opencourse(request, user)
    # Si la petición es GET, retorna la lista de cursos aperturados del profesor
    elif request.method == 'GET':
        return _list_professor_opencourses(request, user)


# Función auxiliar para crear un nuevo curso aperturado y sus horarios asociados
def _create_opencourse(request, user):
    """
    Crea un nuevo curso aperturado (OpenCourse) y sus horarios asociados (Schedule).
    """
    try:
        # Obtiene la instancia del profesor autenticado
        professor = get_object_or_404(models.Professor, email=user.email)

        # Copia los datos recibidos y agrega el id del profesor
        open_course_data = request.data.copy()
        open_course_data['id_professor'] = professor.id_professor

        # Verifica que se haya enviado el campo 'schedule'
        if 'schedule' not in open_course_data:
            return Response({"error": "Se requiere el campo 'schedule'"}, status=400)
        
        # Verifica que el curso especificado exista
        print("open_course_data['id_course']")
        print(open_course_data['id_course'])
        get_object_or_404(models.Course, id_course=open_course_data['id_course'])
        print("PASS")

        # Serializa y valida los datos del curso aperturado
        open_course_serializer = serializers.OpenCourseSerializer(data=open_course_data)
        if not open_course_serializer.is_valid():
            return Response(open_course_serializer.errors, status=400)

        # Guarda el curso aperturado en la base de datos
        open_course_instance = open_course_serializer.save()

        # Obtiene la lista de horarios a crear
        schedule_data = open_course_data['schedule']

        # Crea cada horario asociado al curso aperturado
        for schedule_item in schedule_data:
            schedule_item['id_open_course'] = open_course_instance.id_open_course
            schedule_serializer = serializers.ScheduleSerializer(data=schedule_item)

            # Si algún horario no es válido, elimina el curso aperturado y retorna el error
            if not schedule_serializer.is_valid():
                open_course_instance.delete()
                return Response(schedule_serializer.errors, status=400)

            # Guarda el horario en la base de datos
            schedule_serializer.save()

        # Obtiene todos los horarios creados para el curso aperturado
        schedules_from_db = models.Schedule.objects.filter(id_open_course=open_course_instance.id_open_course)
        all_schedules_serializer = serializers.ScheduleSerializer(instance=schedules_from_db, many=True)

        # Prepara la respuesta con los datos del curso aperturado y sus horarios
        open_course_response = open_course_serializer.data.copy()
        open_course_response["schedule"] = all_schedules_serializer.data

        return Response(open_course_response, status=201)

    except models.Course.DoesNotExist:
        # Error si el curso especificado no existe
        return Response({"error": "El curso especificado no existe"}, status=404)
    except models.Professor.DoesNotExist:
        # Error si el profesor no existe
        return Response({"error": "Profesor no encontrado"}, status=404)
    except Exception as e:
        # Error genérico para cualquier otro problema
        return Response({"error": f"Error interno del servidor: {str(e)}"}, status=500)


# Función auxiliar para listar los cursos aperturados por el profesor autenticado, incluyendo sus horarios
def _list_professor_opencourses(request, user):
    """
    Retorna la lista de cursos aperturados por el profesor autenticado, incluyendo sus horarios.
    """
    try:
        # Obtiene la instancia del profesor autenticado
        professor = get_object_or_404(models.Professor, email=user.email)
        
        # Obtiene todos los cursos aperturados por el profesor
        open_courses = models.OpenCourse.objects.filter(id_professor=professor.id_professor)
        response_data = []
        
        # Para cada curso aperturado, serializa sus datos y los de sus horarios
        for open_course in open_courses:
            open_course_serializer = serializers.OpenCourseSerializer(instance=open_course)
            schedules = models.Schedule.objects.filter(id_open_course=open_course.id_open_course)
            schedule_serializer = serializers.ScheduleSerializer(instance=schedules, many=True)
            open_course_data = open_course_serializer.data.copy()
            open_course_data["schedule"] = schedule_serializer.data
            response_data.append(open_course_data)
        
        # Retorna la lista de cursos aperturados con sus horarios
        return Response(response_data, status=200)
    
    except Exception as e:
        # Error genérico para cualquier otro problema
        return Response({"error": f"Error interno del servidor: {str(e)}"}, status=500) 