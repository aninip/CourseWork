from django.contrib import admin
from .models import Route, Point, RoutePoint

class RoutePointInline(admin.TabularInline):
    model = RoutePoint
    extra = 1

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    inlines = [RoutePointInline]

admin.site.register(Point)
