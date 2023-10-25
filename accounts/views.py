from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, get_user_model
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views import View

from .models import *
from .forms import *
from django.http import JsonResponse, HttpResponse
import csv
import zipfile
from io import BytesIO


def main_page(request):
    return render(request, 'main_page.html')


class CustomLoginView(LoginView):
    template_name = 'auth/login.html'  # Path to your login template


def register(request):
    if request.method == 'POST':
        # Get the user input
        email = request.POST.get('email')
        name = request.POST.get('name')
        city = request.POST.get('city')
        country = request.POST.get('country')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password == confirm_password:
            # Create the Institution instance
            institution = get_user_model().objects.create_user(
                email=email,
                # Set other fields
                password=password,
            )
            # You can also log the institution in here if desired
            return redirect('login')  # Redirect to login page after successful registration
        else:
            error_message = "Passwords do not match. Please try again."
            return render(request, 'auth/register.html', {'error_message': error_message})

    return render(request, 'auth/register.html')


@login_required
def dashboard(request):
    user = request.user
    # Add logic to fetch user-related data and render the dashboard
    return render(request, 'dashboard/dashboard.html', {'user': user})


def teachers(request):
    teachers = Teacher.objects.filter(institution=request.user)

    if request.method == 'POST':
        form = TeacherForm(request.POST)
        if form.is_valid():
            form.save(commit=True, user=request.user)
            return redirect('teachers')  # Redirect to the same page after creating a teacher
    else:
        form = TeacherForm()
    return render(request, 'dashboard/teachers.html', {'form': form, 'teachers': teachers})


def teacher_list(request):
    teachers = Teacher.objects.filter(institution=request.user.id)

    if request.method == 'POST':
        teacher_id = request.POST.get('teacher_id')
        teacher = Teacher.objects.get(pk=teacher_id)
        teacher.delete()
        return redirect('teachers')  # Redirect to teacher list page after deletion

    form = TeacherForm()
    return render(request, 'dashboard/teachers.html', {'teachers': teachers, 'form': form})


def delete_teacher(request, teacher_id):
    teacher = get_object_or_404(Teacher, pk=teacher_id)
    if request.method == 'POST':
        teacher.delete()
    return redirect('teachers')  # Redirect back to the teacher creation page


def students(request):
    students = Student.objects.filter(institution=request.user)

    if request.method == 'POST':
        form = StudentForm(request.user, request.POST)  # Pass the user to the form
        if form.is_valid():
            form.save(commit=True, user=request.user)
            return redirect('students')
    else:
        form = StudentForm()

    return render(request, 'dashboard/students.html', {'student_form': form, 'students': students})


def delete_student(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    if request.method == 'POST':
        student.delete()
    return redirect('students')  # Redirect back to the teacher creation page


def categories(request, age_category_id):
    institution = request.user
    age_category = AgeCategory.objects.get(id=age_category_id)
    game_categories = age_category.gamecategory_set.all()
    students = Student.objects.filter(institution=institution)
    teachers = Teacher.objects.filter(institution=institution)
    teams = Team.objects.all()

    if request.method == 'POST':
        # Check the form data and handle the logic accordingly
        if 'students' in request.POST:
            student_ids = request.POST.getlist('students')
            game_category_id = request.POST.get('game_category')
            team_game_id = request.POST.get('game')

            # Create a new team
            team_name = request.POST.get('name')
            teacher_id = request.POST.get('teacher')

            new_team = Team.objects.create(
                name=team_name,
                institution=institution,
                game_id=team_game_id,
                teacher_id=teacher_id
            )

            # Iterate over selected students and assign them to the team
            for student_id in student_ids:
                student = Student.objects.get(id=student_id)
                student.team = new_team  # Set the team field in the Student model
                student.save()

                # Create StudentGameCategory instance after setting the team field
                student_game_category = StudentGameCategory.objects.create(
                    student=student,
                    game_category_id=game_category_id,
                    team_game_id=team_game_id,
                    teacher_id=teacher_id
                )
                student_game_category.save()

            # Update the current count for the team game
            game = TeamGame.objects.get(id=team_game_id)
            game.current += 1
            game.save()

            return redirect('categories', age_category_id=age_category_id)

        else:
            # Handle individual categories logic
            # Extract form data from the request
            student_ids = request.POST.getlist('students')
            game_category_id = request.POST.get('game_category')
            game_id = request.POST.get('game')
            individual_game_id = request.POST.get('individual_game', None)
            team_game_id = request.POST.get('team_game', None)

            selected_students = request.POST.getlist(f'students_for_{game_id}')
            teacher_id = request.POST.get('teacher')

            # Iterate through selected student IDs and create StudentGameCategory objects
            for student_id in selected_students:
                student_game_category = StudentGameCategory(
                    student_id=student_id,
                    game_category_id=game_category_id,
                    individual_game_id=game_id,
                    teacher_id=teacher_id
                )
                student_game_category.save()

            game = IndividualGame.objects.get(id=game_id)
            game.current += len(selected_students)
            game.save()

            return redirect('categories', age_category_id=age_category_id)


    context = {
        'age_category': age_category,
        'age_category_id': age_category_id,
        'game_categories': game_categories,
        'students': students,
        'teachers': teachers,
        'teams': teams,
    }

    return render(request, 'dashboard/elem.html', context)



def delete_sgc(request, studentgamecategory_id, age_category_id):
    sgc = get_object_or_404(StudentGameCategory, pk=studentgamecategory_id)
    if request.method == 'POST':
        sgc.individual_game.current -= 1
        sgc.individual_game.save()

        sgc.delete()

    return redirect('categories', age_category_id=age_category_id)


def delete_team(request, team_id, age_category_id):
    team = get_object_or_404(Team, pk=team_id)
    if request.method == 'POST':
        students_in_team = StudentGameCategory.objects.filter(
            Q(team_game=team.game_id))

        # Delete corresponding StudentGameCategory instances
        students_in_team.delete()

        # Now delete the team
        team.delete()

    return redirect('categories',  age_category_id=age_category_id)  # Redirect back to the teacher creation page


def dashboard(request):
    # Retrieve individual games and team games
    age_categories = AgeCategory.objects.all()
    game_categories = GameCategory.objects.all()
    individual_games = IndividualGame.objects.all()
    team_games = TeamGame.objects.all()

    # Calculate available places for individual games
    for game in individual_games:
        game.available = game.max_participants - game.current
        game.save()

    # Calculate available places for team games
    for game in team_games:
        game.available = game.max_teams - game.current
        game.save()


    context = {
        'age_categories': age_categories,
        'game_categories': game_categories,
        'ind_games': individual_games,
        'team_games': team_games,
    }

    return render(request, 'dashboard/dashboard.html', context)





