# Generated by Django 3.2.22 on 2023-11-02 21:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0013_alter_profile_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='image',
            field=models.ImageField(default='blank-profile-picture', upload_to='images/'),
        ),
    ]
