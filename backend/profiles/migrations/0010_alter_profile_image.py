# Generated by Django 3.2.22 on 2023-10-12 11:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0009_alter_profile_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='image',
            field=models.ImageField(default='../banner_rzae6b', upload_to='images/'),
        ),
    ]