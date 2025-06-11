from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('id_student', 'first_name', 'last_name', 'email', 'phone', 'created_at')
    search_fields = ('id_student', 'first_name', 'last_name', 'email')
    list_filter = ('created_at',)
