from django.urls import path
from django.views.generic import ListView, DetailView
from .models import Routes
from . import views, models
from django.contrib import admin
urlpatterns = [
    path("", views.index, name='index'),
    path("generate", views.create, name='create'),
    path('admin/', admin.site.urls),
]
