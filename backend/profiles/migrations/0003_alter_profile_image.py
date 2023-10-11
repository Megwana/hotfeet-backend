# Generated by Django 3.2.22 on 2023-10-11 12:31

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0002_alter_profile_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='image',
            field=cloudinary.models.CloudinaryField(default='../blank-profile-picture-973460_1280_fxozyw', max_length=255, verbose_name='image'),
        ),
    ]