from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from api import models, serializers
from datetime import datetime


# Vista para que un profesor pueda adjuntar (POST) o listar (GET) asistencia de un curso aperturado
@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def professor_attendance(request):
    user = request.user
    
    # Verifica que el usuario autenticado sea un profesor
    if not hasattr(user, 'professor'):
        return Response({"error": "Solo los profesores pueden acceder a este recurso."}, status=403)
    
    # Crear Asistencia
    if request.method == 'POST':
        return _create_professor_attendance(request, user)
    # Ver Asistencia
    elif request.method == 'GET':
        return _list_professor_attendance(request, user)


# Función auxiliar para crear asistencia de un curso aperturado usando id_enroll_student
def _create_professor_attendance(request, user):
    """
    Crea una asistencia para un alumno inscrito en un curso aperturado usando id_enroll_student.
    Valida que la inscripción exista y que pertenezca a un curso del profesor autenticado.
    Valida que la fecha de la asistencia sea válida.
    Valida que la asistencia sea válida.
    """
    try:
        data = request.data.copy()
        id_enroll_student = data.get('id_enroll_student')
        date_attendance = data.get('date')
        attendance_value = data.get('attendance')

        # Validar campos requeridos
        if not id_enroll_student or not date_attendance or attendance_value is None:
            return Response({"error": "Se requieren los campos 'id_enroll_student', 'date' y 'attendance'."}, status=400)

        # Validar que la inscripción exista
        enroll = models.EnrollStudent.objects.filter(id_enroll_student=id_enroll_student).first()
        if not enroll:
            return Response({"error": f"La inscripción con id {id_enroll_student} no existe."}, status=404)

        # Obtener el curso aperturado desde la inscripción
        open_course = enroll.id_open_course

        # Validar que el curso aperturado exista (ya está implícito si existe la inscripción)
        if not open_course:
            return Response({"error": "El curso aperturado asociado a la inscripción no existe."}, status=404)

        # Validar que el curso pertenezca al profesor autenticado
        professor = models.Professor.objects.filter(email=user.email).first()
        if not professor or open_course.id_professor_id != professor.id_professor:
            return Response({"error": "No tiene permisos para registrar asistencia en este curso aperturado."}, status=403)

        # Validar que la fecha esté dentro del rango del curso
        if not (str(open_course.start_class) <= date_attendance <= str(open_course.end_class)):
            return Response({"error": "La fecha de asistencia está fuera del rango de fechas del curso."}, status=400)

        # Validar que la fecha corresponda a un día de la semana permitido en el horario del curso
        date_obj = datetime.strptime(date_attendance, "%Y-%m-%d")
        day_week = date_obj.weekday()
        allowed_days = models.Schedule.objects.filter(id_open_course=open_course.id_open_course).values_list('day_week', flat=True)
        if day_week not in allowed_days:
            return Response({"error": "La fecha de asistencia no corresponde a un día de clase según el horario del curso."}, status=400)

        # Validar que el valor de asistencia sea válido
        if int(attendance_value) not in [0, 1, 2]:
            return Response({"error": "El valor de asistencia no es válido. Debe ser 0 (Presente), 1 (Ausente) o 2 (Tardanza)."}, status=400)

        # Evitar duplicados: solo una asistencia por inscripción y fecha
        if models.Attendance.objects.filter(id_enroll_student=enroll, date=date_attendance).exists():
            return Response({"error": "Ya existe una asistencia registrada para este alumno en esta fecha."}, status=400)

        # Crear la asistencia
        attendance_data = {
            'id_enroll_student': enroll.id_enroll_student,
            'date': date_attendance,
            'attendance': attendance_value
        }
        serializer = serializers.AttendanceSerializer(data=attendance_data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        serializer.save()
        
        return Response(serializer.data, status=201)
    except Exception as e:
        return Response({"error": f"Error interno del servidor: {str(e)}"}, status=500)


# Función auxiliar para listar asistencia de un curso aperturado
def _list_professor_attendance(request, user):
    """
    Dado el id de un curso aperturado (open_course), retorna la lista de asistencia de ese curso.
    Valida que el curso aperturado exista y que pertenezca al profesor autenticado.
    """
    try:
        id_open_course = request.query_params.get('id_open_course') or request.data.get('id_open_course')
        if not id_open_course:
            return Response({"error": "Se requiere el campo 'id_open_course' como query param o en el body."}, status=400)

        # Validar que el curso aperturado exista
        open_course = models.OpenCourse.objects.filter(id_open_course=id_open_course).first()
        if not open_course:
            return Response({"error": f"El curso aperturado con id {id_open_course} no existe."}, status=404)

        # Validar que el curso pertenezca al profesor autenticado
        professor = models.Professor.objects.filter(email=user.email).first()
        if not professor or open_course.id_professor_id != professor.id_professor:
            return Response({"error": "No tiene permisos para ver la asistencia de este curso aperturado."}, status=403)

        # Obtener todas las matrícula(s) de estudiantes a ese curso aperturado
        enrollments = models.EnrollStudent.objects.filter(id_open_course=id_open_course)
        enroll_ids = [enroll.id_enroll_student for enroll in enrollments]

        # Obtener todas las asistencias de esos estudiantes en ese curso
        attendances = models.Attendance.objects.filter(id_enroll_student__in=enroll_ids)
        serializer = serializers.AttendanceSerializer(attendances, many=True)
        return Response(serializer.data, status=200)
    except Exception as e:
        return Response({"error": f"Error interno del servidor: {str(e)}"}, status=500)


# Vista para que un estudiante pueda listar su asistencia en un curso aperturado
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def student_attendance(request):
    user = request.user

    # Verifica que el usuario autenticado sea un estudiante
    if not hasattr(user, 'student'):
        return Response({"error": "Solo los estudiantes pueden acceder a este recurso."}, status=403)

    # Obtener el id_enroll_student de los parámetros de la petición
    id_enroll_student = request.query_params.get('id_enroll_student') or request.data.get('id_enroll_student')
    if not id_enroll_student:
        return Response({"error": "Se requiere el campo 'id_enroll_student' como query param o en el body."}, status=400)

    # Obtener el estudiante autenticado
    student = get_object_or_404(models.Student, email=user.email)

    # Buscar la matrícula del estudiante en ese curso aperturado
    enroll = models.EnrollStudent.objects.filter(id_student=student.id_student, id_enroll_student=id_enroll_student).first()
    if not enroll:
        return Response({"error": "No se encontró matrícula para el estudiante en el curso aperturado especificado."}, status=404)

    # Obtener todas las asistencias de esa matrícula
    attendances = models.Attendance.objects.filter(id_enroll_student=enroll.id_enroll_student)
    serializer = serializers.AttendanceSerializer(attendances, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)
