# Generated by Django 5.2.3 on 2025-06-17 03:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_remove_course_unique_course_per_study_plan_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='study_plan',
            field=models.PositiveSmallIntegerField(choices=[(2001, '2001'), (2015, '2015'), (2019, '2019')]),
        ),
    ]
