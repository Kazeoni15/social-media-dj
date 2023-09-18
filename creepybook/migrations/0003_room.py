# Generated by Django 4.2.4 on 2023-09-16 06:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('creepybook', '0002_remove_userprofile_location'),
    ]

    operations = [
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField(unique=True)),
            ],
        ),
    ]
