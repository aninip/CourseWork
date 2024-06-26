# Generated by Django 5.0.4 on 2024-04-24 15:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('naturetrail', '0005_routes_first_alter_routes_level_of_hardness_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Points',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='generated-route', max_length=320)),
                ('description', models.TextField()),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
            ],
        ),
    ]
