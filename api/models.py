from datetime import date
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.db import models
from django.shortcuts import get_object_or_404
import re

class Professor(User):
    # username ! (email)
    # first_name
    # last_name
    # email
    # password !
    # groups
    # user_permissions
    # is_staff
    # is_active
    # date_joined

    id_professor = models.AutoField(primary_key=True)

    phone = models.CharField(
        max_length=9,
        validators=[
            RegexValidator(
                regex=r'^\d{9}$',
                message='El número de teléfono debe tener exactamente 9 dígitos'
            )
        ],
        unique=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Validamos la estructura correcta del email y colocamos que el username sea el mismo que el email
    def save(self, *args, **kwargs):
        if self.email:
            if not re.match(r'^\w{5,15}@unfv\.edu\.pe$', self.email):
                raise ValueError("El email debe tener el formato: entre 5 y 15 caracteres seguidos de '@unfv.edu.pe'")
        if self.email:
            self.username = self.email
        super().save(*args, **kwargs)

    def __str__(self):
        return self.get_full_name()

    class Meta:
        verbose_name = "Professor"
        verbose_name_plural = "Professors"


class Student(User):
    id_student = models.AutoField(primary_key=True)

    phone = models.CharField(
        max_length=9,
        validators=[
            RegexValidator(
                regex=r'^\d{9}$',
                message='El número de teléfono debe tener exactamente 9 dígitos'
            )
        ],
        unique=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Validamos la estructura correcta del email y colocamos que el username sea el mismo que el email
    def save(self, *args, **kwargs):
        if self.email:
            if not re.match(r'^\d{10}@unfv\.edu\.pe$', self.email):
                raise ValueError("El email debe tener el formato: 10 dígitos seguidos de '@unfv.edu.pe'")
        if self.email:
            self.username = self.email
        super().save(*args, **kwargs)

    def __str__(self):
        return self.get_full_name()

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"


class Course(models.Model):
    STUDY_PLAN_CHOICES = [
        (2001, 2001),
        (2015, 2015),
        (2019, 2019),
    ]
    COURSE_TYPE_CHOICES = [
        ('Electivo', 'Electivo'),
        ('Obligatorio', 'Obligatorio'),
    ]
    STUDY_TYPE_CHOICES = [
        ('Especialidad', 'Especialidad'),
        ('Específico', 'Específico'),
        ('General', 'General'),
    ]

    id_course = models.AutoField(primary_key=True)
    name = models.CharField(
        max_length=100
    )
    study_cycle = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ]
    )
    credits = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(8)
        ]
    )
    duration_weeks = models.PositiveSmallIntegerField(
        default=16,
        validators=[
            MinValueValidator(4),
            MaxValueValidator(20)
        ]
    )
    theory_hours = models.PositiveSmallIntegerField(blank=True, default=0)
    practice_hours = models.PositiveSmallIntegerField(blank=True, default=0)
    
    study_plan = models.PositiveSmallIntegerField(
        choices=STUDY_PLAN_CHOICES
    )
    subject_code = models.PositiveIntegerField(
        unique=True,
        validators=[
            MinValueValidator(1000),
            MaxValueValidator(99999999)
        ]
    )
    course_type = models.CharField(
        choices=COURSE_TYPE_CHOICES,
        default="Obligatorio"
    )
    study_type = models.CharField(
        choices=STUDY_TYPE_CHOICES,
        default="Especialidad"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Course"
        verbose_name_plural = "Courses"


class OpenCourse(models.Model):
    PROFESSIONAL_CAREER_CHOICES = [
        ("Ingeniería Informática","Ingeniería Informática"),
        ("Ingeniería de Telecomunicaciones","Ingeniería de Telecomunicaciones"),
        ("Ingeniería Electrónica","Ingeniería Electrónica"),
        ("Ingeniería Mecatrónica","Ingeniería Mecatrónica"),
    ]
    SECTION_CHOICES = [
        ('A','A'),
        ('B','B'),
        ('C','C'),
        ('D','D'),
    ]

    id_open_course = models.AutoField(primary_key=True)
    id_professor = models.ForeignKey('Professor', on_delete=models.CASCADE)
    id_course = models.ForeignKey('Course', on_delete=models.CASCADE)
    
    start_class = models.DateField()
    end_class = models.DateField()
    
    academic_year = models.PositiveSmallIntegerField(
        default=date.today().year
    )
    academic_semester = models.SmallIntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(4)
        ],
        default=1
    )
    
    professional_career = models.CharField(
        choices=PROFESSIONAL_CAREER_CHOICES
    )
    section = models.CharField(
        choices=SECTION_CHOICES,
        default='A'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.id_course} ({self.academic_year}-{self.academic_semester}) | {self.id_professor}"

    class Meta:
        verbose_name = "OpenCourse"
        verbose_name_plural = "OpenCourses"


class Schedule(models.Model):
    DAY_WEEK_CHOICES = [
        (0, 'Lunes'),
        (1, 'Martes'),
        (2, 'Miércoles'),
        (3, 'Jueves'),
        (4, 'Viernes'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]

    id_schedule = models.AutoField(primary_key=True)
    id_open_course = models.ForeignKey(OpenCourse, on_delete=models.CASCADE, related_name='schedules')

    day_week = models.SmallIntegerField(
        choices=DAY_WEEK_CHOICES
    )
    start_hour = models.TimeField()
    end_hour = models.TimeField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # Buscar el nombre del día correspondiente al valor de day_week
        day_name = dict(self.DAY_WEEK_CHOICES).get(self.day_week, self.day_week)
        return f"{self.id_open_course} | {day_name} {self.start_hour} {self.end_hour}"

    class Meta:
        verbose_name = "Schedule"
        verbose_name_plural = "Schedules"


class EnrollStudent(models.Model):
    id_enroll_student = models.AutoField(primary_key=True)

    id_student = models.ForeignKey(Student, on_delete=models.CASCADE)
    id_open_course = models.ForeignKey(OpenCourse, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id_student} | {self.id_open_course}"

    class Meta:
        verbose_name = "EnrollStudent"
        verbose_name_plural = "EnrollStudents"


class Attendance(models.Model):
    ATTENDANCE_CHOICES = [
        (0, 'Presente'),
        (1, 'Ausente'),
        (2, 'Tardanza'),
    ]

    id_attendance = models.AutoField(primary_key=True)
    id_enroll_student = models.ForeignKey(EnrollStudent, on_delete=models.CASCADE)

    date = models.DateField()
    attendance = models.SmallIntegerField(
        choices=ATTENDANCE_CHOICES,
        default=0
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id_enroll_student} | {self.date} | {self.attendance}"

    class Meta:
        verbose_name = "Attendance"
        verbose_name_plural = "Attendances"


