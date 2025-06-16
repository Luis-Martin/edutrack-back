from django.contrib import admin
from api import models

@admin.register(models.Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('id_professor', 'username', 'first_name', 'last_name', 'email', 'phone', 'created_at', 'updated_at', 'password')
    search_fields = ('id_student', 'first_name', 'last_name', 'email')
    list_filter = ('created_at','updated_at')
