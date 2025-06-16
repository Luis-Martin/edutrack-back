from rest_framework import serializers
from api import models

class ProfessorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Professor
        fields = [
            'id_professor',
            'username',
            'first_name',
            'last_name',
            'email',
            'phone',
            'created_at',
            'updated_at',
        ]
