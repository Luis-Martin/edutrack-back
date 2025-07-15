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


# Función auxiliar para crear asistencia de un curso aperturado usando id_enroll_student (ahora acepta lista)
def _create_professor_attendance(request, user):
    """
    Crea asistencias para varios alumnos inscritos en un curso aperturado usando una lista de id_enroll_student.
    Valida que las inscripciones existan y que pertenezcan a un curso del profesor autenticado.
    Valida que la fecha de la asistencia sea válida.
    Valida que la asistencia sea válida.
    Además, marca como falta (attendance=1) a los alumnos inscritos en el curso que no estén en el array id_enroll_student para esa fecha.
    """
    try:
        data = request.data.copy()
        id_enroll_student_list = data.get('id_enroll_student')
        date_attendance = data.get('date')
        attendance_value = data.get('attendance')

        # Validar campos requeridos
        if not id_enroll_student_list or not date_attendance or attendance_value is None:
            return Response({"error": "Se requieren los campos 'id_enroll_student', 'date' y 'attendance'."}, status=400)

        # Asegurarse de que id_enroll_student_list sea una lista
        if not isinstance(id_enroll_student_list, list):
            # Si viene como string separado por comas, intentar convertirlo
            if isinstance(id_enroll_student_list, str):
                try:
                    id_enroll_student_list = [int(x.strip()) for x in id_enroll_student_list.split(",")]
                except Exception:
                    return Response({"error": "El campo 'id_enroll_student' debe ser una lista de IDs."}, status=400)
            else:
                id_enroll_student_list = [id_enroll_student_list]

        # Validar que la lista no esté vacía
        if not id_enroll_student_list:
            return Response({"error": "La lista de 'id_enroll_student' no puede estar vacía."}, status=400)

        # Validar que todas las inscripciones existan
        enrolls = list(models.EnrollStudent.objects.filter(id_enroll_student__in=id_enroll_student_list))
        enrolls_map = {e.id_enroll_student: e for e in enrolls}
        not_found = [eid for eid in id_enroll_student_list if eid not in enrolls_map]
        if not_found:
            return Response({"error": f"Las inscripciones con id(s) {not_found} no existen."}, status=404)

        # Validar que todas las inscripciones pertenezcan al mismo curso aperturado
        open_course_ids = set(e.id_open_course.id_open_course for e in enrolls)
        if len(open_course_ids) != 1:
            return Response({"error": "Todas las inscripciones deben pertenecer al mismo curso aperturado."}, status=400)
        open_course_id = open_course_ids.pop()
        open_course = enrolls[0].id_open_course

        # Validar que el curso aperturado exista (ya está implícito si existen las inscripciones)
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

        # Obtener todos los id_enroll_student del curso aperturado
        all_enrolls = list(models.EnrollStudent.objects.filter(id_open_course=open_course.id_open_course))
        all_enroll_ids = [e.id_enroll_student for e in all_enrolls]

        # Evitar duplicados: solo una asistencia por inscripción y fecha
        already_exists = list(
            models.Attendance.objects.filter(
                id_enroll_student__in=all_enroll_ids,
                date=date_attendance
            ).values_list('id_enroll_student', flat=True)
        )
        if already_exists:
            return Response({"error": f"Ya existe una asistencia registrada para los alumnos con id_enroll_student: {already_exists} en esta fecha."}, status=400)

        # Crear las asistencias para los alumnos presentes (los que están en id_enroll_student_list)
        created_attendances = []
        errors = []
        for eid in id_enroll_student_list:
            attendance_data = {
                'id_enroll_student': eid,
                'date': date_attendance,
                'attendance': attendance_value
            }
            serializer = serializers.AttendanceSerializer(data=attendance_data)
            if serializer.is_valid():
                serializer.save()
                created_attendances.append(serializer.data)
            else:
                errors.append({"id_enroll_student": eid, "errors": serializer.errors})

        # Crear las asistencias para los alumnos ausentes (los que NO están en id_enroll_student_list)
        absent_ids = [eid for eid in all_enroll_ids if eid not in id_enroll_student_list]
        for eid in absent_ids:
            attendance_data = {
                'id_enroll_student': eid,
                'date': date_attendance,
                'attendance': 1  # 1 = Ausente
            }
            serializer = serializers.AttendanceSerializer(data=attendance_data)
            if serializer.is_valid():
                serializer.save()
                created_attendances.append(serializer.data)
            else:
                errors.append({"id_enroll_student": eid, "errors": serializer.errors})

        if errors:
            return Response({
                "created": created_attendances,
                "errors": errors
            }, status=207 if created_attendances else 400)

        return Response(created_attendances, status=201)
    except Exception as e:
        return Response({"error": f"Error interno del servidor: {str(e)}"}, status=500)

# Función auxiliar para listar asistencia de un curso aperturado
def _list_professor_attendance(request, user):
    """
    Dado el id de un curso aperturado (open_course), retorna la lista de asistencia de ese curso,
    agrupada por matrícula (id_enroll_student), incluyendo los datos completos del estudiante y la lista de asistencias.
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

        # Obtener todas las matrículas de estudiantes a ese curso aperturado
        enrollments = models.EnrollStudent.objects.filter(id_open_course=id_open_course).select_related('id_student')
        enroll_ids = [enroll.id_enroll_student for enroll in enrollments]

        # Mapear enrollments por id para acceso rápido
        enroll_map = {enroll.id_enroll_student: enroll for enroll in enrollments}

        # Obtener todas las asistencias de esos estudiantes en ese curso
        attendances = models.Attendance.objects.filter(id_enroll_student__in=enroll_ids)

        # Agrupar asistencias por matrícula
        from collections import defaultdict
        attendance_by_enroll = defaultdict(list)
        for att in attendances:
            attendance_by_enroll[att.id_enroll_student_id].append(att)

        # Preparar respuesta agrupada
        from api import serializers  # Importar aquí para evitar import circular
        result = []
        for enroll_id in enroll_ids:
            enroll = enroll_map[enroll_id]
            student = enroll.id_student
            # Serializar todos los campos del estudiante
            student_data = serializers.StudentSerializer(student).data
            # Serializar asistencias de esta matrícula
            attendance_list = []
            for att in attendance_by_enroll.get(enroll_id, []):
                attendance_list.append({
                    "id_attendance": att.id_attendance,
                    "date": att.date,
                    "attendance": att.attendance,
                    "created_at": att.created_at,
                    "updated_at": att.updated_at
                })
            result.append({
                "id_enroll_student": enroll_id,
                "student": student_data,
                "attendance": attendance_list
            })

        return Response(result, status=200)
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
