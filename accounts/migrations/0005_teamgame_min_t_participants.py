# Generated by Django 4.2.6 on 2023-10-23 12:44

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0004_teacher_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="teamgame",
            name="min_t_participants",
            field=models.PositiveIntegerField(default=2),
            preserve_default=False,
        ),
    ]