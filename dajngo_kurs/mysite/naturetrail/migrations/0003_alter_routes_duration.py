# Generated by Django 4.2.1 on 2023-06-06 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('naturetrail', '0002_alter_routes_level_of_hardness'),
    ]

    operations = [
        migrations.AlterField(
            model_name='routes',
            name='duration',
            field=models.PositiveSmallIntegerField(),
        ),
    ]
