# Generated by Django 5.2.3 on 2025-06-17 03:49

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_alter_course_practice_hours_and_more'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='course',
            name='unique_course_per_study_plan',
        ),
        migrations.AlterField(
            model_name='course',
            name='subject_code',
            field=models.PositiveIntegerField(unique=True, validators=[django.core.validators.MinValueValidator(1000), django.core.validators.MaxValueValidator(99999999)]),
        ),
    ]
