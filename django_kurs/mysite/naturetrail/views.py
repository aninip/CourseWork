import random as rand
from datetime import time, datetime
from django.shortcuts import render
from .forms import RoutesForm
from .models import Routes


def index(request):
    return render(request, 'homePage.html')
def create(request):
    error = " "
    if request.method == 'POST':
        Routes.objects.filter(first=False).delete()
        form = RoutesForm(request.POST)
        if form.is_valid():
            generated_form = form.save(commit=False)
            # Выборка записей маршрутов по сложности и времени
            level_of_hardness = form.cleaned_data.get("level_of_hardness")
            duration = form.cleaned_data.get("duration")
            matching_routes = Routes.objects.filter(
                level_of_hardness=level_of_hardness,
                duration=duration)
            if matching_routes.exists():
                generated_route = rand.choice(matching_routes)

                generated_form.name = generated_route.name
                generated_form.description = generated_route.description
                generated_form.water = generated_route.water
                generated_form.picture = generated_route.picture
                generated_form.equipment = generated_route.equipment
                generated_form.save()
            else:
                # не найдено соответствующих маршрутов
                pass
        else:
            # Обработка некорректной формы
            print(form.errors.as_data())
            error = 'Данные некорректны'

    nash = Routes.objects.last()
    form = RoutesForm()
    data = {
        'form': form,
        'error': error,
        'description_h': nash.description,
        'picture_h': nash.picture,
        'name_h': nash.name,
        'dificult_h': nash.level_of_hardness,
        'water_h': nash.water,
        'duration_h': nash.duration,
    }
    return render(request, 'includes/some_html.html', data)
