from django.contrib import admin
import zipfile
from io import StringIO
from django.http import HttpResponse
from .models import *

def download_game_csv(request, game_id):
    # Get the game and associated students (assuming you have the logic for this)
    game = IndividualGame.objects.get(id=game_id)
    students = StudentGameCategory.objects.filter(individual_game=game)

    # Prepare CSV data
    csv_data = StringIO()
    csv_data.write("last_name,name,patronymic,institution_name\n")

    for student in students:
        csv_data.write(f"{student.student.last_name},{student.student.name},{student.student.patronymic},{student.student.institution.name}\n")

    # Encode the CSV data as bytes
    csv_data_bytes = csv_data.getvalue().encode('utf-8')

    # Create a zip file and add the CSV file to it
    zip_buffer = StringIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        zip_file.writestr(f'game_{game.id}.csv', csv_data_bytes)

    # Build the response and set headers for file download
    response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename=game_{game.id}.zip'

    return response



download_game_csv.short_description = 'Download CSV for Individual Games'

class DAdmin(admin.ModelAdmin):
    actions = [download_game_csv]

admin.site.register(IndividualGame, DAdmin)

admin.site.register(Institution)
admin.site.register(Teacher)
admin.site.register(Student)
admin.site.register(AgeCategory)
admin.site.register(GameCategory)
# admin.site.register(IndividualGame)
admin.site.register(TeamGame)
admin.site.register(Team)
admin.site.register(StudentGameCategory)

