from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from api import models, serializers


# Vista para que un profesor pueda adjuntar (POST) o listar (GET) alumnos en un curso aperturado
@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def professor_enrollstudent(request):
    user = request.user
    
    # Verifica que el usuario autenticado sea un profesor
    if not hasattr(user, 'professor'):
        return Response({"error": "Solo los profesores pueden acceder a este recurso."}, status=403)
    
    # Adjuntar a un alumno a un Curso
    if request.method == 'POST':
        return _create_professor_enrollstudent(request, user)
    # Ver los alumno adjuntos a un Curso
    elif request.method == 'GET':
        return _list_professor_enrollstudent(request, user)


# Función auxiliar para adjuntar estudiantes a un curso aperturado
def _create_professor_enrollstudent(request, user):
    try:
        # Obtiene la instancia del profesor autenticado
        professor = get_object_or_404(models.Professor, email=user.email)

        enrollstudent_data = request.data.copy()

        # Validar que se reciban los ids requeridos
        id_student = enrollstudent_data.get("id_student")
        id_open_course = enrollstudent_data.get("id_open_course")

        if id_student is None or id_open_course is None:
            return Response(
                {"error": "Se requieren los campos 'id_student' y 'id_open_course'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validar estudiante existente
        student = models.Student.objects.filter(id_student=id_student).first()
        if not student:
            return Response(
                {"error": f"El estudiante con id {id_student} no existe."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Validar Curso aperturado existente
        open_course = models.OpenCourse.objects.filter(id_open_course=id_open_course).first()
        if not open_course:
            return Response(
                {"error": f"El curso aperturado con id {id_open_course} no existe."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = serializers.EnrollStudentSerializer(data=enrollstudent_data)

        # Valida los datos del enrollstudent
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Adjuntar Alumno a Curso
        enrollstudent = serializer.save()

        # Serializar el enrollstudent creado para devolver todos los campos
        enrollstudent_serializer = serializers.EnrollStudentSerializer(enrollstudent)

        # Retorna todos los campos del modelo EnrollStudent
        return Response(enrollstudent_serializer.data, status=status.HTTP_201_CREATED)

    except Exception as e:
        # Error genérico para cualquier otro problema
        return Response({"error": f"Error interno del servidor: {str(e)}"}, status=500)


# Función auxiliar para listar los estudiantes adjuntos a los cursos aperturados por el profesor
def _list_professor_enrollstudent(request, user):
    """
    Dado el id de un curso aperturado (open_course), retorna la lista de alumnos inscritos en ese curso.
    Valida que el curso aperturado exista y que pertenezca al profesor autenticado.
    El id del curso aperturado se obtiene como query parameter (?open_course=...).
    """
    from rest_framework import status

    try:
        # Obtener el id del curso aperturado desde los query parameters
        open_course_id = request.query_params.get("open_course", None)

        if open_course_id is None:
            return Response(
                {"error": "Se requiere el parámetro 'open_course' en la URL."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validar que el curso aperturado exista
        open_course = models.OpenCourse.objects.filter(id_open_course=open_course_id).first()
        if not open_course:
            return Response(
                {"error": f"El curso aperturado con id {open_course_id} no existe."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Validar que el curso aperturado le pertenezca al profesor autenticado
        professor = models.Professor.objects.filter(email=user.email).first()
        if not professor:
            return Response(
                {"error": "Profesor autenticado no encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )

        if open_course.id_professor_id != professor.id_professor:
            return Response(
                {"error": "No tiene permisos para ver los estudiantes de este curso aperturado."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Obtener todas las inscripciones de estudiantes a ese curso aperturado
        enrollments = models.EnrollStudent.objects.filter(id_open_course=open_course_id)

        # Para cada inscripción, incluir la información del estudiante
        result = []
        for enrollment in enrollments:
            # Serializar la inscripción
            enrollment_data = serializers.EnrollStudentSerializer(enrollment).data

            # Obtener y serializar el estudiante
            student = models.Student.objects.filter(id_student=enrollment.id_student_id).first()
            if student:
                student_data = serializers.StudentSerializer(student).data
            else:
                student_data = None

            # Reemplazar el campo id_student por el objeto student
            enrollment_data["student"] = student_data
            if "id_student" in enrollment_data:
                del enrollment_data["id_student"]

            result.append(enrollment_data)

        return Response(result, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": f"Error interno del servidor: {str(e)}"}, status=500)


# Vista para que un alumno pueda ver cursos al cual está adjuntado (GET)
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def student_enrollstudent(request):
    """
    Permite a un estudiante ver sus inscripciones a cursos aperturados.
    Si se pasa un id_enroll_student, devuelve solo esa inscripción como objeto.
    Si no, devuelve todas las inscripciones como lista.
    """
    user = request.user

    # Verifica que el usuario autenticado sea un estudiante
    if not hasattr(user, 'student'):
        return Response({"error": "Solo los estudiantes pueden acceder a este recurso."}, status=403)

    # Obtener el estudiante autenticado
    student = get_object_or_404(models.Student, email=user.email)

    # Obtener el id_enroll_student desde query_params o body (GET)
    id_enroll_student = _get_id_enroll_student_from_request(request)

    if id_enroll_student:
        # Si se pasa un id_enroll_student, devolver solo ese objeto
        enrollment_obj = _get_enrollment_object(id_enroll_student, student)
        if isinstance(enrollment_obj, Response):
            return enrollment_obj  # Error response
        return Response(enrollment_obj, status=status.HTTP_200_OK)
    else:
        # Si no se pasa id, devolver todas las inscripciones como lista
        enrollments_list = _get_all_enrollments_list(student)
        return Response(enrollments_list, status=status.HTTP_200_OK)


def _get_id_enroll_student_from_request(request):
    """
    Intenta obtener el id_enroll_student desde query_params o body en una petición GET.
    """
    id_enroll_student = request.query_params.get("id_enroll_student")
    if id_enroll_student is None:
        try:
            import json
            if request.body:
                body_data = json.loads(request.body.decode('utf-8'))
                id_enroll_student = body_data.get("id_enroll_student")
        except Exception:
            id_enroll_student = None
    return id_enroll_student


def _get_enrollment_object(id_enroll_student, student):
    """
    Devuelve un solo objeto de inscripción enriquecido, o un Response de error si no existe.
    """
    from api import serializers
    try:
        enrollment = models.EnrollStudent.objects.get(
            id_enroll_student=id_enroll_student,
            id_student=student.id_student
        )
    except models.EnrollStudent.DoesNotExist:
        return Response(
            {"error": f"No se encontró la inscripción con id_enroll_student={id_enroll_student} para este estudiante."},
            status=404
        )

    open_course = enrollment.id_open_course
    professor = open_course.id_professor
    course = open_course.id_course

    open_course_data = serializers.OpenCourseSerializer(open_course).data if open_course else None
    professor_data = serializers.ProfessorSerializer(professor).data if professor else None
    course_data = serializers.CourseSerializer(course).data if course else None

    return {
        "id_enroll_student": enrollment.id_enroll_student,
        "id_student": enrollment.id_student.id_student if hasattr(enrollment.id_student, 'id_student') else enrollment.id_student,
        "open_course": open_course_data,
        "professor": professor_data,
        "course": course_data,
        "academic_year": open_course.academic_year if open_course else None,
        "academic_semester": open_course.academic_semester if open_course else None,
        "section": open_course.section if open_course else None,
        "created_at": enrollment.created_at,
        "updated_at": enrollment.updated_at,
    }


def _get_all_enrollments_list(student):
    """
    Devuelve una lista de objetos de inscripciones enriquecidas para el estudiante.
    """
    from api import serializers
    enrollments = models.EnrollStudent.objects.filter(id_student=student.id_student)
    enriched_enrollments = []
    for enrollment in enrollments:
        open_course = enrollment.id_open_course
        professor = open_course.id_professor
        course = open_course.id_course

        open_course_data = serializers.OpenCourseSerializer(open_course).data if open_course else None
        professor_data = serializers.ProfessorSerializer(professor).data if professor else None
        course_data = serializers.CourseSerializer(course).data if course else None

        enriched_enrollments.append({
            "id_enroll_student": enrollment.id_enroll_student,
            "id_student": enrollment.id_student.id_student if hasattr(enrollment.id_student, 'id_student') else enrollment.id_student,
            "open_course": open_course_data,
            "professor": professor_data,
            "course": course_data,
            "academic_year": open_course.academic_year if open_course else None,
            "academic_semester": open_course.academic_semester if open_course else None,
            "section": open_course.section if open_course else None,
            "created_at": enrollment.created_at,
            "updated_at": enrollment.updated_at,
        })
    return enriched_enrollments


# Vista para que un profesor pueda eliminar alumnos en un curso aperturado
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def professor_deleteenrollstudent(request):
    """
    Elimina la inscripción de un alumno (id_student) en un curso aperturado (id_open_course).
    Solo profesores autenticados pueden realizar esta acción.
    """
    from api import models
    from django.shortcuts import get_object_or_404
    from rest_framework.response import Response

    user = request.user

    # Verifica que el usuario autenticado sea un profesor
    if not hasattr(user, 'professor'):
        return Response({"error": "Solo los profesores pueden acceder a este recurso."}, status=403)

    id_student = request.data.get("id_student")
    id_open_course = request.data.get("id_open_course")

    if not id_student or not id_open_course:
        return Response({"error": "Se requieren los campos 'id_student' y 'id_open_course'."}, status=400)

    # Verifica que el curso aperturado pertenezca al profesor autenticado
    open_course = get_object_or_404(models.OpenCourse, id_open_course=id_open_course)
    if open_course.id_professor.id_professor != user.professor.id_professor:
        return Response({"error": "No tiene permisos para modificar este curso."}, status=403)

    # Busca la inscripción
    try:
        enrollment = models.EnrollStudent.objects.get(id_student=id_student, id_open_course=id_open_course)
    except models.EnrollStudent.DoesNotExist:
        return Response({"error": "La inscripción no existe."}, status=404)

    # Elimina la inscripción
    enrollment.delete()
    return Response({"message": "Inscripción eliminada correctamente."}, status=200)