from django.db import models


class Routes(models.Model):
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
    picture = models.ImageField(upload_to='images')
    equipment = models.FileField(upload_to='equipments')
    water = models.CharField(max_length=320)
    first = models.BooleanField(default=False)

    def __str__(self):
        return self.name
