import random as rand
from datetime import time, datetime
from django.shortcuts import render
from naturetrail.forms import RoutesForm
from .models import Route, Point


def index(request):
    return render(request, 'homePage.html')


def create(request):
    error = ""
    if request.method == 'POST':
        handle_post_request(request.POST)
    nash = Route.objects.last()
    form = RoutesForm()
    queryset = Point.objects.all()
    all_points = [{"name": point.name, "longitude": point.longitude, "latitude":point.latitude} for point in queryset]
    print(all_points)
    data = prepare_data(nash, form, error, all_points)
    return render(request, 'route_generator.html', data)


def handle_post_request(post_data):
    Route.objects.filter(first=False).delete()
    form = RoutesForm(post_data)
    if form.is_valid():
        save_generated_route(form)
    else:
        handle_invalid_form(form)


def save_generated_route(form):
    generated_form = form.save(commit=False)
    level_of_hardness = form.cleaned_data.get("level_of_hardness")
    duration = form.cleaned_data.get("duration")
    matching_routes = Route.objects.filter(
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


def prepare_data(nash, form, error,all_points):
    return {
        'form': form,
        'error': error,
        'description_h': nash.description,
        'picture_h': nash.picture,
        'name_h': nash.name,
        'dificult_h': nash.level_of_hardness,
        'water_h': nash.water,
        'duration_h': nash.duration,
        'all_points': all_points,
    }
def route_detail(request, route_id):
    try:
        route = Route.objects.get(pk=route_id)
        data = prepare_data_for_ready_route(route)
    except Route.DoesNotExist:
        return render(request, 'error.html', {'error_message': 'Маршрут не найден'})

    return render(request, 'route_detail.html', data)
def prepare_data_for_ready_route(_route):
    return {
        'form': "form",
        'description_h': _route.description,
        'picture_h': _route.picture,
        'name_h': _route.name,
        'dificult_h': _route.level_of_hardness,
        'water_h': _route.water,
        'duration_h': _route.duration,
    }