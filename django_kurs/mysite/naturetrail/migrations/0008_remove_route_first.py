# Generated by Django 5.0.4 on 2024-05-15 15:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('naturetrail', '0007_route_routepoint_delete_routes_rename_points_point_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='route',
            name='first',
        ),
    ]
