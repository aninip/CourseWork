from django.urls import path
from django.views.generic import ListView, DetailView
from .models import Route
from . import views, models
from django.contrib import admin
urlpatterns = [
    path("", views.index, name='index'),
    path("generate/", views.create, name='create'),
    path('route/<int:route_id>/', views.route_detail, name='route_detail'),
    path('admin/', admin.site.urls),
    path('routeq/', views.submit_points, name='submit_points'),
]
