# Generated by Django 5.2.3 on 2025-06-17 19:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_course_course_type_course_professional_career_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='professional_career',
            field=models.CharField(choices=[('Ingeniería Informática', 'Ingeniería Informática'), ('Ingeniería de Telecomunicaciones', 'Igeniería de Telecomunicaciones'), ('Ingeniería Mecatrónica', 'Igeniería Mecatrónica'), ('Ingeniería Eléctrica', 'Igeniería Eléctrica')]),
        ),
    ]
