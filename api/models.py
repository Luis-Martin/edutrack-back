from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.db import models
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
            if not re.match(r'^\d{10}@unfv\.edu\.pe$', self.email):
                raise ValueError("El email debe tener el formato: 10 dígitos seguidos de '@unfv.edu.pe'")
        if self.email:
            self.username = self.email
        super().save(*args, **kwargs)

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

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"


class Course(models.Model):
    STUDY_PLAN_CHOICES = [
        (2001, '2001'),
        (2015, '2015'),
        (2019, '2019'),
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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Course"
        verbose_name_plural = "Courses"
