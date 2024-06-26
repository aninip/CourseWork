from django.db import models

class Route(models.Model):
    DIFICULT_CHOICES = (
        ("Лёгкий", "Лёгкий"),
        ("Средний", "Средний"),
        ("Сложный", "Сложный"),
        ("Выживание", "Выживание"),
    )
    name = models.CharField(max_length=320, default='generated-route')
    duration = models.PositiveSmallIntegerField()
    level_of_hardness = models.CharField(max_length=20,
                                         choices=DIFICULT_CHOICES, )
    description = models.TextField()
    price_of_accommodation = models.PositiveSmallIntegerField(default=0)
    picture = models.ImageField(upload_to='naturetrail/static/images', null=True)
    equipment = models.FileField(upload_to='naturetrail/static/equipments',null=True)
    water = models.CharField(max_length=320)
    points = models.ManyToManyField('Point', through='RoutePoint')


class Point(models.Model):
    name = models.CharField(max_length=320, default='generated-point')
    description = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    order = models.PositiveSmallIntegerField()
    closest_accomodation = models.CharField(max_length=100, default='none')
    def __str__(self):
        return f"Name: {self.name}, Description: {self.description}, Latitude: {self.latitude}, Longitude: {self.longitude}"
class RoutePoint(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    point = models.ForeignKey(Point, on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField()
    def __str__(self):
        return f"Route: {self.route.name}, Point: {self.point.name}, Order: {self.order}"