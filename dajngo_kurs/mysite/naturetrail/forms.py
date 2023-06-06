from .models import Routes
from django.forms import ModelForm,TextInput


class RoutesForm(ModelForm):
    class Meta:
        model = Routes
        fields = ['level_of_hardness', 'duration']

        widgets = {

            "level_of_hardness": TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Сложность маршрута'
            }),
            "duration": TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Продолжительность маршрута'
            })
        }
