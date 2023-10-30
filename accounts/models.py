from django.contrib.auth.models import AbstractUser, BaseUserManager, Group
from django.db import models
from django.utils.timezone import now
from django.utils import timezone
from django.core.exceptions import ValidationError


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class Institution(AbstractUser):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    region = models.CharField(max_length=50, default="")
    country = models.CharField(max_length=50)
    postcode = models.CharField(max_length=100)
    groups = models.ManyToManyField(Group)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'address', 'city', 'region', 'country', 'postcode']

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def get_username(self):
        return self.email

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email.split('@')[0]
        super().save(*args, **kwargs)


class Teacher(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, null=True, blank=True)
    last_name = models.CharField(max_length=100, default="")
    name = models.CharField(max_length=100, default="")
    patronymic = models.CharField(max_length=100, default="")
    date_of_birth = models.DateField()
    status = models.BooleanField(default=False)

    def __str__(self):
        first_name_initial = self.name[0] if self.name else ""
        patronymic_initial = self.patronymic[0] if self.patronymic else ""
        return f"{self.last_name} {first_name_initial}. {patronymic_initial}."


class AgeCategory(models.Model):
    name = models.CharField(max_length=50)
    min_age = models.IntegerField()
    max_age = models.IntegerField()

    def __str__(self):
        return f"{self.name} ({self.min_age}-{self.max_age})"


class GameCategory(models.Model):
    name = models.CharField(max_length=50)
    age_category = models.ForeignKey(AgeCategory, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} - {self.age_category.name}"


class IndividualGame(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(GameCategory, on_delete=models.CASCADE)
    min_age = models.IntegerField(default=0)
    max_age = models.IntegerField(default=0)
    max_participants = models.PositiveIntegerField()
    current = models.PositiveIntegerField(default=0)
    available = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.category.name}) - {self.min_age}-{self.max_age}"


class TeamGame(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(GameCategory, on_delete=models.CASCADE)
    min_age = models.IntegerField(default=0)
    max_age = models.IntegerField(default=0)
    min_t_participants = models.PositiveIntegerField()
    max_t_participants = models.PositiveIntegerField()
    max_teams = models.PositiveIntegerField()
    current = models.PositiveIntegerField(default=0)
    available = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.category.name}) - {self.min_age}-{self.max_age}"


class Team(models.Model):
    name = models.CharField(max_length=100)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    game = models.ForeignKey(TeamGame, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Student(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, null=True, blank=True)
    last_name = models.CharField(max_length=100, default="")
    name = models.CharField(max_length=100, default="")
    patronymic = models.CharField(max_length=100, default="")
    date_of_birth = models.DateField()
    age_category = models.ForeignKey('AgeCategory', on_delete=models.CASCADE)

    def __str__(self):
        first_name_initial = self.name[0] if self.name else ""
        patronymic_initial = self.patronymic[0] if self.patronymic else ""
        return f"{self.last_name} {first_name_initial}. {patronymic_initial}."


class StudentGameCategory(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    game_category = models.ForeignKey(GameCategory, on_delete=models.CASCADE)
    individual_game = models.ForeignKey(IndividualGame, on_delete=models.CASCADE, null=True, blank=True)
    team_game = models.ForeignKey(TeamGame, on_delete=models.CASCADE, null=True, blank=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, default=None)

    class Meta:
        unique_together = ('student', 'game_category')

class TeamParticipant(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)  # Assuming you have a Team model
    student = models.ForeignKey(Student, on_delete=models.CASCADE)  # Assuming you have a Student model

    def __str__(self):
        return f"{self.team.name} - {self.student.name} {self.student.last_name}"
