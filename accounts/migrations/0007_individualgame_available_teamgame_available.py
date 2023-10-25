# Generated by Django 4.2.6 on 2023-10-25 10:48

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0006_remove_student_teacher_studentgamecategory_teacher"),
    ]

    operations = [
        migrations.AddField(
            model_name="individualgame",
            name="available",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="teamgame",
            name="available",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
