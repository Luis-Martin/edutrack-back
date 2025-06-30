from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from api import models, serializers


@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def professor_opencourse(request):
    user = request.user
    
    # Verifica que el usuario autenticado sea un profesor
    if not hasattr(user, 'professor'):
        return Response({"error": "Solo los profesores pueden acceder a este recurso."}, status=403)
    
    # Crear un Curso
    if request.method == 'POST':
        return _create_opencourse(request, user)
    # Obtener los Cursos Aperturados
    elif request.method == 'GET':
        return _list_professor_opencourses(request, user)


def _create_opencourse(request, user):
    try:
        
        professor = get_object_or_404(models.Professor, email=user.email)
        
        if 'open_course' not in request.data: return Response({"error": "Se requiere el campo 'open_course'"}, status=400)
        if 'schedule' not in request.data: return Response({"error": "Se requiere el campo 'schedule'"}, status=400)
        
        open_course_data = request.data['open_course'].copy()
        open_course_data['id_professor'] = professor.id_professor
        
        if 'id_course' not in open_course_data:
            return Response({"error": "Se requiere el campo 'id_course'"}, status=400)
        
        course = get_object_or_404(models.Course, id_course=open_course_data['id_course'])
        open_course_serializer = serializers.OpenCourseSerializer(data=open_course_data)
        
        if not open_course_serializer.is_valid():
            return Response(open_course_serializer.errors, status=400)
        
        open_course_instance = open_course_serializer.save()
        schedule_data = request.data['schedule']
        
        for schedule_item in schedule_data:
            schedule_item['id_open_course'] = open_course_instance.id_open_course
            schedule_serializer = serializers.ScheduleSerializer(data=schedule_item)
            if not schedule_serializer.is_valid():
                open_course_instance.delete()
                return Response(schedule_serializer.errors, status=400)
            schedule_serializer.save()
        
        schedules_from_db = models.Schedule.objects.filter(id_open_course=open_course_instance.id_open_course)
        all_schedules_serializer = serializers.ScheduleSerializer(instance=schedules_from_db, many=True)
        
        open_course_response = open_course_serializer.data.copy()
        open_course_response["schedule"] = all_schedules_serializer.data
        
        return Response(open_course_response, status=201)
    
    except models.Course.DoesNotExist:
        return Response({"error": "El curso especificado no existe"}, status=404)
    except models.Professor.DoesNotExist:
        return Response({"error": "Profesor no encontrado"}, status=404)
    except Exception as e:
        return Response({"error": f"Error interno del servidor: {str(e)}"}, status=500)


def _list_professor_opencourses(request, user):
    try:
        professor = get_object_or_404(models.Professor, email=user.email)
        open_courses = models.OpenCourse.objects.filter(id_professor=professor.id_professor)
        response_data = []
        for open_course in open_courses:
            open_course_serializer = serializers.OpenCourseSerializer(instance=open_course)
            schedules = models.Schedule.objects.filter(id_open_course=open_course.id_open_course)
            schedule_serializer = serializers.ScheduleSerializer(instance=schedules, many=True)
            open_course_data = open_course_serializer.data.copy()
            open_course_data["schedule"] = schedule_serializer.data
            response_data.append(open_course_data)
        return Response(response_data, status=200)
    except Exception as e:
        return Response({"error": f"Error interno del servidor: {str(e)}"}, status=500) 