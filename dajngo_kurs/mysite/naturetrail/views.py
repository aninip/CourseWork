import random as rand
from datetime import time, datetime

from django.shortcuts import render
from django.http import HttpResponse
from .forms import RoutesForm
from .models import Routes
# Create your views here.
def index(request):
    return render(request, 'homePage.html')

def create(request):
    error = ''
    if request.method == 'POST':
        all_records = Routes.objects.all()
        for val in all_records:
            if val.first == False:
                val.delete()
        form = RoutesForm(request.POST)
        if form.is_valid():
            generated_form = form.save(commit=False)
            #print(form)
            print(all_records)
            #print('Введенная сложность',form.cleaned_data.get("level_of_hardness"))
            temp_duration = form.cleaned_data.get("duration");
            #print('Введенная продолжительность',form.cleaned_data.get("duration"))
            #print('temp_duration-', temp_duration)
            dificult_list = []  # здесь храним названия подходящих по сложности маршрутов
            duration_list = []  # десь храним названия подходящих по сложности и времени маршрутов
            for val in all_records:
                if val.name != 'generated-route':
                    if form.cleaned_data.get("level_of_hardness") == val.level_of_hardness:
                        dificult_list.append(val)
            for val in dificult_list:
                if form.cleaned_data.get("duration") == val.duration:
                    duration_list.append(val.name)
            #print('подходящие по сложности', dificult_list)
            print('подходящие по времени', duration_list)
            generates_route = rand.choice(duration_list)
            for val in all_records:
                if val.name== generates_route:
                    disc =val.description
                    voda = val.water
                    pic = val.picture
                    equip = val.equipment
                    break

            print('Готовый маршрут название', generates_route)
            final_route_disc = duration_list[duration_list.index(generates_route)]
            # form=generates_route
            now = datetime.now()
            current_time = now.strftime("/%H%M%S")
            namess= generates_route + current_time

            generated_form.name = generates_route #+ current_time
            generated_form.description = disc
            generated_form.water = voda
            generated_form.picture = pic
            generated_form.equipment = equip
            generated_form.save()

        else:
            print(form.errors.as_data())
            error ='Данные не корректны'

    nash =Routes.objects.last()
    form = RoutesForm()
    data = {
        'form': form,
        'error': error,
        'description_h' : nash.description,
        'picture_h': nash.picture,
        'name_h' : nash.name,
        'dificult_h' : nash.level_of_hardness,
        'water_h' : nash.water,
        'duration_h':nash.duration,
    }
    return render(request,'includes/some_html.html',data)