import random as rand
import os
import requests
# from datetime import time, datetime
from django.shortcuts import render,redirect
from naturetrail.forms import RoutesForm
from .models import Route, Point, RoutePoint
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from dotenv import load_dotenv
from django.conf import settings
from django.core.files.base import ContentFile



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
    queryset = Point.objects.all()
    unique_points = set()
    all_points = []

    for point in queryset:
        # Создаем уникальный ключ для каждой точки
        unique_key = (point.name, point.longitude, point.latitude)
        
        # Если уникальный ключ не встречался ранее, добавляем точку в список
        if unique_key not in unique_points:
            unique_points.add(unique_key)
            all_points.append({
                "name": point.name,
                "longitude": point.longitude,
                "latitude": point.latitude,
                "description": point.description,
                "order": point.order,
                "closest_accomodation": point.closest_accomodation,
            })

    return render(request, 'route_generator.html', {'all_points': all_points})

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
    equipment_file = _route.equipment
    points_data = [{'name': point.name, 'latitude': point.latitude, 'longitude': point.longitude} for point in points]
    return {
        'form': "form",
        'description_h': _route.description,
        'picture_h': picture_path,
        'name_h': _route.name,
        'dificult_h': _route.level_of_hardness,
        'water_h': _route.water,
        'duration_h': _route.duration,
        'points_data': json.dumps(points_data),
        'equipment_content': equipment_file
    }


def get_default_points(level_of_hardness, duration):
    queryset = Point.objects.all()
    unique_points = set()
    all_points = []

    for point in queryset:
        # Создаем уникальный ключ для каждой точки
        unique_key = (point.name, point.longitude, point.latitude)
        
        # Если уникальный ключ не встречался ранее, добавляем точку в список
        if unique_key not in unique_points:
            unique_points.add(unique_key)
            all_points.append({
                "name": point.name,
                "longitude": point.longitude,
                "latitude": point.latitude,
                "description": point.description,
                "order": point.order,
                "closest_accomodation": point.closest_accomodation,
            })
# Функция для поиска точки по имени
    def find_point_by_name(name):
        for point in all_points:
            if point['name'] == name:
                return point
        return None
    
    if level_of_hardness == "Лёгкий":
            return [
                find_point_by_name("Центральная Усадьба"),
                find_point_by_name("Двуглавая сопка Перья")
            ]
    elif level_of_hardness == "Средний":
            return [
                find_point_by_name("Центральная Усадьба"),
                find_point_by_name("Двуглавая сопка Перья"),
                find_point_by_name("Приют Гремучий ключ"),
                find_point_by_name("Митькины скалы")
            ]
    elif level_of_hardness == "Сложный":
            return [
                find_point_by_name("Центральная Усадьба"),
                find_point_by_name("Двуглавая сопка Перья"),
                find_point_by_name("Приют Гремучий ключ"),
                find_point_by_name("Митькины скалы"),
                find_point_by_name("Круглица"),
                find_point_by_name("Приют Таганай"),
            ]
    elif level_of_hardness == "Выживание":
            return [
                find_point_by_name("Центральная Усадьба"),
                find_point_by_name("Чёрная скала"),
                find_point_by_name("Двуглавая сопка Перья"),
                find_point_by_name("Приют Гремучий ключ"),
                find_point_by_name("Митькины скалы"),
                find_point_by_name("Круглица"),
                find_point_by_name("Приют Таганай"),
                find_point_by_name("Дальний Таганай"),
            ]
 
    return []

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
            
            print(data)

            if not points:
                points = get_default_points(level_of_hardness, duration)
                print("точки по дефолту",points)

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
                # print(generated_name, generated_description)
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
            print(mocked_route)
            
            equipment_file = None
            if duration == '1':
                equipment_file = '1day_list.pdf'
            else:
                equipment_file = 'bazovyj-chek-list-dlya-peshego-pohoda.pdf'

            # Чтение содержимого файла снаряжения
            equipment_path = os.path.join(settings.BASE_DIR, r'D:\CourseWork\django_kurs\mysite\equipments', equipment_file)
            with open(equipment_path, 'rb') as file:
                equipment_content = file.read()

             # Создание маршрута в базе данных
            new_route = Route.objects.create(
                name=generated_name,
                duration=duration,
                level_of_hardness=level_of_hardness,
                description=generated_description,
                price_of_accommodation=1000,
                water='',
                picture=None,
                # equipment=None
            )
            new_route.equipment.save(equipment_file, ContentFile(equipment_content), save=True)

            # # Добавление точек в маршрут
            # for idx, point in enumerate(points):
            #     new_point = Point.objects.create(
            #         name=point.get('name', 'Unnamed Point'),
            #         description=point.get('description', ''),
            #         latitude=point.get('latitude', 0),
            #         longitude=point.get('longitude', 0),
            #         order=idx + 1,
            #         closest_accomodation=point.get('closest_accomodation', '')
            #     )
            #     # Создание связи между маршрутом и точкой с указанием порядка
            #     RoutePoint.objects.create(
            #         route=new_route,
            #         point=new_point,
            #         order=idx + 1
            #     )
            #     new_route.points.add(new_point)
            

            for idx, point in enumerate(points):
                point_name = point.get('name', 'Unnamed Point')
                point_description = point.get('description', '')
                point_latitude = point.get('latitude', 0)
                point_longitude = point.get('longitude', 0)
                point_order = idx + 1
                point_closest_accommodation = point.get('closest_accommodation', '')

                # Проверяем, существует ли точка с такими же координатами в базе данных
                existing_point = Point.objects.filter(
                    name=point_name,
                    latitude=point_latitude,
                    longitude=point_longitude
                ).first()

                if existing_point:
                    new_point = existing_point
                    # print("найдена точка с названием " + existing_point.name)
                else:
                    print("создана новая точка!!!!!!!!!!99999999")
                    new_point = Point.objects.create(
                        name=point_name,
                        description=point_description,
                        latitude=point_latitude,
                        longitude=point_longitude,
                        order=point_order,
                        closest_accommodation=point_closest_accommodation
                    )

                # Создание связи между маршрутом и точкой с указанием порядка
                RoutePoint.objects.create(
                    route=new_route,
                    point=new_point,
                    order=idx + 1
                )
                new_route.points.add(new_point)


            print("id машрута",new_route.id)
            return JsonResponse({'status': 'success', 'message': 'Route created', 'route_id': new_route.id})
    
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)