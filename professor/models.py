from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.hashers import make_password

# Create your models here.
class Professor(models.Model):
    # Auto-incrementing ID (Django's default)
    id_professor = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    
    # Email validation for UNFV format
    email = models.EmailField(
        max_length=200,
        validators=[
            RegexValidator(
                regex=r'^\d{10}@unfv\.edu\.pe$',
                message='El email debe tener el formato: 2020011111@unfv.edu.pe'
            )
        ],
        unique=True
    )
    
    # Phone validation for exactly 9 digits
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
    
    # Password field with hashing
    password = models.CharField(max_length=200)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Hash the password before saving
        if self.password and not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)
