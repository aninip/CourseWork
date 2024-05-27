import random as rand
import os
import requests
from datetime import time, datetime
from django.shortcuts import render
from naturetrail.forms import RoutesForm
from .models import Route, Point
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from dotenv import load_dotenv

SYSTEM_PROMPT = '''Я хочу, чтобы ты отвечал исключительно в формате json. Ты будешь помогать составлять маршруты для похода по парку Таганай.

Форма ответа:
{
"name": "",
"description": ""
}

Я буду использовать тебя в качестве метода в программе. Я буду отправлять тебе json вида:
{
  "points": [
{
      "name": "Двуглавая сопка Перья",
       "description": "Самая южная вершина хребта Большой Таганай. Находится в 13 км к ССВ от Златоуста. Название дано исследователем Южного Урала В.П.Сементовским за характерную разрезанность вершины сопки надвое.На южном и юго-западном склонах Двуглавой сопки альпийские луга, березовое криволесье, заросли горца альпийского и черничника. На южном склоне расположен так называемый Скалодром, используемый альпинистами в качестве полигона для тренировок. Южная вершина сопки называется «Перья» за характерные формы составляющих ее скал. Ее высота 1034 м. Северная вершина достигает высоты 1041 м. Представляет собой дугообразный гребень, вытянутый в юго-восточном направлении. Склоны покрыты многочисленными россыпями. Вершина состоит из многочисленных террас, скальных стенок и расщелин. Туристы называют эту вершину Бараньими лбами. У подножия Двуглавой сопки – многочисленные ключи, среди которых наиболее известен Белый Ключ на юго-восточном склоне. Западный и южный склоны сопки спускаются в долину реки Большая Тесьма. Восточный – в сравнительно неширокую меридионально расположенную долину, отделяющую хребты Большой и Средний Таганай. ",
       "closest_accomodation": "Приют "Белый ключ""
       "latitude": 55.270849,
      "longitude": 59.774707
    },
    { "name": "Круглица", "closest_accomodation": "Приют "Таганай"", "description":"Центральная вершина хребта Большой Таганай, наивысшая точка (1178м) всего Таганайского горного массива. Название получила за характерную округлую форму. Вершина Круглицы за сходство с тюркским головным убором называется Башкирской шапкой. Гора сложена белыми, розовыми, вишневыми кварцитами с включением авантюрина, иногда массивного, но чаще такой же полосчатопятнистой структуры, как и в других местах Таганая. У восточного поножия Круглицы расположен туристический приют «Таганай», от которого на вершину горы идет 3-километровая пешеходная тропа. Однако подъем на вершину достаточно сложен, так как в верхней своей трети Круглица почти полностью покрыта каменными осыпями-курумами, передвигаться по которым небезопасно. ", "latitude": 55.315571, "longitude": 59.841536 },
    ,
    {
      "name": "Центральная Усадьба",
      "description":"Центральная усадьба – это главные ворота парка, у которых берут свое начало все официальные маршруты по Таганаю. Отсюда начинаются Верхняя и Нижняя тропы."
      "closest_accomodation": "Центральная Усадьба"
      "latitude": 55.221322,
      "longitude": 59.731765
    }
  ],
  "level": "Сложный",
  "duration": "3",
  "number_participants": "2",
  "season": "Весна",
  "accommodation": "В доме"
}

Это описание требований к маршруту. там указаны точки, которые хочет посетить пользователь, количество людей, сложность желаемая, продолжительность в днях, время года и предпочитаемый вид ночлега.

Придумывай исходя из этого маршрут по форме ответа: который я указал. Если среди точек нет центральной усадьбы, возвращай ошибку, все маршруты всегда начинаются там. И выходить люди будут там. Название должно быть таким, чтобы все маршруты имели свое уникальное имя, а не "Маршрут по Таганаю". Эпитеты например. На основании точек в маршруте.

Вот как должно выглядеть поле description. В описании тоже описывай именно маршрут. Нужно описать нормальными словами, через какие точки он проходит, немного про эти точки. В конце описания описать почему этот маршрут подходит. Описание делай не таким литературным, как название. Больше конкретики, но и не совсем сухо. Описание разделяй на дни. У каждой точки есть ближайший ночлег. description в формате: сначала краткое описания маршрута в целом. Потом описание по дням (исходя из duration)

Строго придерживайся формы ответа. Возвращай только имя и описание'''

def index(request):
    return render(request, 'homePage.html')


def create(request):
    error = ""
    if request.method == 'POST':
        handle_post_request(request.POST)
    nash = Route.objects.last()
    form = RoutesForm()
    queryset = Point.objects.all()
    all_points = [{"name": point.name, "longitude": point.longitude, "latitude":point.latitude, "description":point.description, "order":point.order, "closest_accomodation": point.closest_accomodation} for point in queryset]
    print(all_points)
    return render(request, 'route_generator.html', {'all_points': all_points})


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
    print(data)
    return render(request, 'route_detail.html', data)

def prepare_data_for_ready_route(_route):
    original_picture_path = _route.picture.name
    to_remove = "naturetrail/static/"
    picture_path = original_picture_path.removeprefix(to_remove)
    points = _route.points.all()
    points_data = [{'name': point.name, 'latitude': point.latitude, 'longitude': point.longitude} for point in points]
    return {
        'form': "form",
        'description_h': _route.description,
        'picture_h': picture_path,
        'name_h': _route.name,
        'dificult_h': _route.level_of_hardness,
        'water_h': _route.water,
        'duration_h': _route.duration,
        'points_data': json.dumps(points_data)

    }

def submit_points(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            points = data.get('points', [])
            level_of_hardness = data.get('level', [])
            duration = data.get('duration', [])
            number_participants = data.get('number_participants', [])
            season = data.get('season', [])
            accommodation = data.get('accommodation', [])

            url = 'https://api.proxyapi.ru/openai/v1/chat/completions'
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer sk-NcHdNV6awcejKqoGBrqFXvEABIisIJT5'
            }
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": str(data)}
                ],
                "temperature": 0.7
            }

            #print(json.dumps(payload))

            response = requests.post(url, headers=headers, data=json.dumps(payload))
            if response.status_code == 200:
                api_response = response.json()
                api_json = json.loads(api_response['choices'][0]['message']['content'])
                generated_name = api_json['name']
                generated_description = api_json['description']
                print(generated_name, generated_description)
            else:
                return JsonResponse({'status': 'error', 'message': 'API request failed'}, status=response.status_code)

            mocked_route = {
                'name': generated_name,
                'description': generated_description,
                'points': points,
                'priceOfAccommodation': accommodation,
                'levelOfHardness': level_of_hardness,
                'duration': duration,
                'numberOfParticipants': number_participants,
                'season': season
            }

            
            return JsonResponse({'status': 'success', 'message': 'Points received', 'data': mocked_route})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)