# Generated by Django 3.2.22 on 2023-10-11 12:20

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='image',
            field=cloudinary.models.CloudinaryField(default='https://res.cloudinary.com/dnkoqrvie/image/upload/v1693398098/blank-profile-picture-973460_1280_fxozyw.webp', max_length=255, verbose_name='image'),
        ),
    ]