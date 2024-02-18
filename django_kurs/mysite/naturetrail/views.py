import random as rand
from datetime import time, datetime
from django.shortcuts import render
from .forms import RoutesForm
from .models import Routes


def index(request):
    return render(request, 'homePage.html')


def create(request):
    error = ""

    if request.method == 'POST':
        handle_post_request(request.POST)

    nash = Routes.objects.last()
    form = RoutesForm()
    data = prepare_data(nash, form, error)
    return render(request, 'includes/some_html.html', data)


def handle_post_request(post_data):
    Routes.objects.filter(first=False).delete()
    form = RoutesForm(post_data)
    if form.is_valid():
        save_generated_route(form)
    else:
        handle_invalid_form(form)


def save_generated_route(form):
    generated_form = form.save(commit=False)
    level_of_hardness = form.cleaned_data.get("level_of_hardness")
    duration = form.cleaned_data.get("duration")
    matching_routes = Routes.objects.filter(
        level_of_hardness=level_of_hardness,
        duration=duration)
    if matching_routes.exists():
        generated_route = rand.choice(matching_routes)
        copy_data_to_generated_form(generated_route, generated_form)
        generated_form.save()
    else:
        # Не найдено соответствующих маршрутов
        pass


def copy_data_to_generated_form(route, generated_form):
    generated_form.name = route.name
    generated_form.description = route.description
    generated_form.water = route.water
    generated_form.picture = route.picture
    generated_form.equipment = route.equipment


def handle_invalid_form(form):
    # Обработка некорректной формы
    print(form.errors.as_data())
    error = 'Данные некорректны'


def prepare_data(nash, form, error):
    return {
        'form': form,
        'error': error,
        'description_h': nash.description,
        'picture_h': nash.picture,
        'name_h': nash.name,
        'dificult_h': nash.level_of_hardness,
        'water_h': nash.water,
        'duration_h': nash.duration,
    }
def route_detail(request, route_id):
    try:
        route = Routes.objects.get(pk=route_id)
    except Routes.DoesNotExist:
        return render(request, 'error.html', {'error_message': 'Маршрут не найден'})

    return render(request, 'route_detail.html', {'route': route})