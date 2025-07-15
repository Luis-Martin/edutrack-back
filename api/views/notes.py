from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from api import models, serializers
from datetime import datetime


# Vista para que un profesor pueda adjuntar (POST) o listar (GET) nota de un curso aperturado
@api_view(['GET', 'POST', 'DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def professor_note(request):
    user = request.user
    
    # Verifica que el usuario autenticado sea un profesor
    if not hasattr(user, 'professor'):
        return Response({"error": "Solo los profesores pueden acceder a este recurso."}, status=403)
    
    # Crear Nota
    if request.method == 'POST':
        return _create_professor_note(request, user)
    # Ver Nota
    elif request.method == 'GET':
        return _list_professor_note(request, user)
    # Borrar Nota
    elif request.method == 'DELETE':
        return _delete_professor_note(request, user)


# Función auxiliar para crear o actualizar nota de un curso aperturado
def _create_professor_note(request, user):
    """
    Dado el id_enroll_student, crea o actualiza una nota para un alumno inscrito en ese curso.
    Si ya existe una nota del mismo tipo para la inscripción, la sobrescribe (PUT).
    Recupera el id_open_course y el id_student a partir del id_enroll_student.
    Valida que el curso aperturado exista y que pertenezca al profesor autenticado.
    Valida que el alumno inscrito exista y que pertenezca al curso aperturado.
    Valida que la nota sea válida.
    """
    try:
        data = request.data.copy()
        id_enroll_student = data.get('id_enroll_student')
        type_note = data.get('type_note')
        note = data.get('note')

        # Validar campos requeridos
        if not id_enroll_student or not type_note or note is None:
            return Response({"error": "Se requieren los campos 'id_enroll_student', 'type_note' y 'note'."}, status=400)

        # Recuperar la inscripción
        enroll = models.EnrollStudent.objects.filter(id_enroll_student=id_enroll_student).first()
        if not enroll:
            return Response({"error": f"La inscripción con id {id_enroll_student} no existe."}, status=404)

        # Recuperar el curso aperturado y el estudiante desde la inscripción
        open_course = enroll.id_open_course
        student = enroll.id_student

        # Validar que el curso aperturado exista (ya está implícito si existe la inscripción)
        if not open_course:
            return Response({"error": f"El curso aperturado asociado a la inscripción no existe."}, status=404)

        # Validar que el curso pertenezca al profesor autenticado
        professor = models.Professor.objects.filter(email=user.email).first()
        if not professor or open_course.id_professor_id != professor.id_professor:
            return Response({"error": "No tiene permisos para registrar nota en este curso aperturado."}, status=403)

        # Validar que la nota sea válida
        try:
            note_value = int(note)
        except (ValueError, TypeError):
            return Response({"error": "La nota debe ser un número entero."}, status=400)
        if note_value < 0 or note_value > 20:
            return Response({"error": "La nota debe estar entre 0 y 20."}, status=400)

        # Buscar si ya existe una nota de este tipo para la inscripción
        existing_note = models.Note.objects.filter(id_enroll_student=id_enroll_student, type_note=type_note).first()

        if existing_note:
            # Si existe, actualiza la nota (PUT)
            serializer = serializers.NoteSerializer(existing_note, data={
                'id_enroll_student': id_enroll_student,
                'type_note': type_note,
                'note': note_value
            }, partial=True)
            if not serializer.is_valid():
                return Response(serializer.errors, status=400)
            serializer.save()
            return Response(serializer.data, status=200)
        else:
            # Si no existe, crea la nota normalmente
            note_data = {
                'id_enroll_student': id_enroll_student,
                'type_note': type_note,
                'note': note_value
            }
            serializer = serializers.NoteSerializer(data=note_data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=400)
            serializer.save()
            return Response(serializer.data, status=201)
    except Exception as e:
        return Response({"error": f"Error interno del servidor: {str(e)}"}, status=500)


# Función auxiliar para listar notas de un curso aperturado
def _list_professor_note(request, user):
    """
    Dado el id de un curso aperturado (open_course), retorna la lista de todas las notas registradas en ese curso,
    agrupadas por alumno (id_enroll_student), incluyendo los datos del estudiante y sus notas.
    El id_open_course se recibe como query parameter.
    """
    try:
        # Obtener id_open_course desde los query params
        id_open_course = request.query_params.get('id_open_course')

        # Validar campo requerido
        if not id_open_course:
            return Response({"error": "Se requiere el campo 'id_open_course' como query param en la URL."}, status=400)

        # Validar que el curso aperturado exista
        open_course = models.OpenCourse.objects.filter(id_open_course=id_open_course).first()
        if not open_course:
            return Response({"error": f"El curso aperturado con id {id_open_course} no existe."}, status=404)

        # Validar que el curso pertenezca al profesor autenticado
        professor = models.Professor.objects.filter(email=user.email).first()
        if not professor or open_course.id_professor_id != professor.id_professor:
            return Response({"error": "No tiene permisos para ver las notas de este curso aperturado."}, status=403)

        # Obtener todas las inscripciones de estudiantes en el curso aperturado
        enrolls = models.EnrollStudent.objects.filter(id_open_course=id_open_course)

        # Para cada inscripción, obtener el estudiante y sus notas
        result = []
        for enroll in enrolls:
            student = enroll.id_student
            # Serializar datos del estudiante (puedes ajustar los campos según tu serializer)
            student_data = serializers.StudentSerializer(student).data if student else None

            # Obtener todas las notas de esta inscripción
            notes = models.Note.objects.filter(id_enroll_student=enroll.id_enroll_student)
            # Serializar las notas, omitiendo el campo id_enroll_student en cada nota
            notes_data = []
            for note in notes:
                note_dict = serializers.NoteSerializer(note).data
                # Eliminar id_enroll_student del dict de la nota
                note_dict.pop('id_enroll_student', None)
                notes_data.append(note_dict)

            result.append({
                "id_enroll_student": enroll.id_enroll_student,
                "studnet": student_data,
                "notes": notes_data
            })

        return Response(result, status=200)
    except Exception as e:
        return Response({"error": f"Error interno del servidor: {str(e)}"}, status=500)


# Función auxiliar para borrar una nota de un curso aperturado

def _delete_professor_note(request, user):
    """
    Elimina una nota específica dado su id_note (query param).
    Valida que la nota exista y que el profesor autenticado tenga permiso para eliminarla.
    """
    try:
        id_note = request.query_params.get('id_note')
        if not id_note:
            return Response({"error": "Se requiere el campo 'id_note' como query param en la URL."}, status=400)

        # Buscar la nota
        note = models.Note.objects.filter(id_note=id_note).first()
        if not note:
            return Response({"error": f"La nota con id {id_note} no existe."}, status=404)

        # Validar que el profesor tenga permiso para borrar la nota
        enroll = note.id_enroll_student
        open_course = enroll.id_open_course if enroll else None
        professor = models.Professor.objects.filter(email=user.email).first()
        if not open_course or not professor or open_course.id_professor_id != professor.id_professor:
            return Response({"error": "No tiene permisos para eliminar esta nota."}, status=403)

        note.delete()
        return Response({"message": f"Nota con id {id_note} eliminada correctamente."}, status=200)
    except Exception as e:
        return Response({"error": f"Error interno del servidor: {str(e)}"}, status=500)


# Vista para que un estudiante pueda listar sus notas usando id_enroll_student como query param
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def student_note(request):
    user = request.user

    # Verifica que el usuario autenticado sea un estudiante
    if not hasattr(user, 'student'):
        return Response({"error": "Solo los estudiantes pueden acceder a este recurso."}, status=403)

    # Obtener el id_enroll_student solo de los query params
    id_enroll_student = request.query_params.get('id_enroll_student')
    if not id_enroll_student:
        return Response({"error": "Se requiere el campo 'id_enroll_student' como query param en la URL."}, status=400)

    # Obtener el estudiante autenticado
    student = models.Student.objects.filter(email=user.email).first()
    if not student:
        return Response({"error": "No se encontró el estudiante autenticado."}, status=404)

    # Buscar la matrícula del estudiante con ese id_enroll_student
    enroll = models.EnrollStudent.objects.filter(id_student=student.id_student, id_enroll_student=id_enroll_student).first()
    if not enroll:
        return Response({"error": "No se encontró matrícula para el estudiante con el id_enroll_student especificado."}, status=404)

    # Obtener todas las notas de esa matrícula
    notes = models.Note.objects.filter(id_enroll_student=enroll.id_enroll_student)
    serializer = serializers.NoteSerializer(notes, many=True)

    return Response(serializer.data, status=200)