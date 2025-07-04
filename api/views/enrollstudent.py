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
    """
    from rest_framework import status

    try:
        # Obtener el id del curso aperturado desde el body
        open_course_id = request.data.get("open_course", None)

        if open_course_id is None:
            return Response(
                {"error": "Se requiere el campo 'open_course'."},
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
        # Obtener el profesor autenticado
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

        # Serializar las inscripciones (EnrollStudent) para devolver todos los campos
        enrollments_serializer = serializers.EnrollStudentSerializer(enrollments, many=True)

        return Response(enrollments_serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": f"Error interno del servidor: {str(e)}"}, status=500)


# Vista para que un alumno pueda ver cursos al cual está adjuntado (POST)
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def student_enrollstudent(request):
    user = request.user

    # Verifica que el usuario autenticado sea un estudiante
    if not hasattr(user, 'student'):
        return Response({"error": "Solo los estudiantes pueden acceder a este recurso."}, status=403)
    
    # Obtener el estudiante autenticado
    student = get_object_or_404(models.Student, email=request.user)
    
    # Obtener todas las inscripciones del estudiante
    enrollments = models.EnrollStudent.objects.filter(id_student=student.id_student)

    # Serializar las inscripciones (EnrollStudent) para devolver todos los campos
    enrollments_serializer = serializers.EnrollStudentSerializer(enrollments, many=True)

    return Response(enrollments_serializer.data, status=status.HTTP_200_OK)
