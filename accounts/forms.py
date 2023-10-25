from django import forms
from .models import *
from django.forms.widgets import DateInput


class NameInput(forms.TextInput):
    input_type = 'text'  # Use a text input type for custom formatting

    def render(self, name, value, attrs=None, renderer=None):
        rendered = super().render(name, value, attrs, renderer)
        return rendered + """
        <script>
            $(document).ready(function() {
                $("#id_%s").on('input', function() {
                    var words = this.value.split(' ');
                    for (var i = 0; i < words.length; i++) {
                        words[i] = words[i].charAt(0).toUpperCase() + words[i].slice(1).toLowerCase();
                    }
                    this.value = words.join(' ');
                });
            });
        </script>
        """ % name

class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['last_name', 'name', 'patronymic', 'date_of_birth', 'status']
        labels = {
            'last_name': 'Фамилия',
            'name': 'Имя',
            'patronymic': 'Отчество',
            'date_of_birth': 'Дата рождения',
            'status': 'Тренер'
        }
        widgets = {
            'date_of_birth': DateInput(attrs={'type': 'date'}),
            'last_name': NameInput(),
            'name': NameInput(),
            'patronymic': NameInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        date_of_birth = cleaned_data.get('date_of_birth')

        if date_of_birth:
            today = timezone.datetime(2024, 5, 10)
            age = today.year - date_of_birth.year - (
                    (today.month, today.day) < (date_of_birth.month, date_of_birth.day))

            if age < 18:
                raise ValidationError("Тренер должен быть не младше 18 лет.")

        return cleaned_data

    def save(self, commit=True, user=None):
        teacher = super().save(commit=False)
        if user:
            teacher.institution = user  # Assign institution correctly
        if commit:
            teacher.save()
        return teacher


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['last_name', 'name', 'patronymic', 'date_of_birth', 'age_category']
        labels = {
            'last_name': 'Фамилия',
            'name': 'Имя',
            'patronymic': 'Отчество',
            'date_of_birth': 'Дата рождения',
            'age_category': 'Возрастная категория',
        }
        widgets = {
            'date_of_birth': DateInput(attrs={'type': 'date'}),
            'last_name': NameInput(),
            'name': NameInput(),
            'patronymic': NameInput(),
        }
    def clean(self):
        cleaned_data = super().clean()
        date_of_birth = cleaned_data.get('date_of_birth')

        if date_of_birth:
            today = timezone.datetime(2024, 5, 10)
            age = today.year - date_of_birth.year - (
                    (today.month, today.day) < (date_of_birth.month, date_of_birth.day))

            if age < 4:
                raise ValidationError("Участник должен быть не младше 4 лет.")

        return cleaned_data

    def save(self, commit=True, user=None):
        student = super().save(commit=False)
        if user:
            student.institution = user  # Assign institution correctly
        if commit:
            student.save()
        return student
