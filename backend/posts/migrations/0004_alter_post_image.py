# Generated by Django 3.2.22 on 2023-11-02 22:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_alter_post_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, default='images/banner_rzae6b', upload_to='images/'),
        ),
    ]
