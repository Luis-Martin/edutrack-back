from django.contrib import admin
from .models import Professor

@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('id_professor', 'first_name', 'last_name', 'email', 'phone', 'created_at')
    search_fields = ('id_professor', 'first_name', 'last_name', 'email')
    list_filter = ('created_at',)
