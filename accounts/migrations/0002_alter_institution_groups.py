# Generated by Django 4.2.5 on 2023-09-25 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="institution",
            name="groups",
            field=models.ManyToManyField(to="auth.group"),
        ),
    ]