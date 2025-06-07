from rest_framework import serializers
from professor.models import Professor

class ProfessorSerilizer(serializers.ModelSerializer):
    class Meta:
        model = Professor
        fields = ('id_professor',
                  'first_name',
                  'last_name',
                  'email',
                  'phone',
                  'password',
                  'created_at',
                  'updated_at')
        read_only_fields = ('created_at',)
