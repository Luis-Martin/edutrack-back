from django.contrib.auth.models import User
from django.core.validators import RegexValidator
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
