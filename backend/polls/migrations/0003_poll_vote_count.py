# Generated by Django 3.2.22 on 2023-10-31 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0002_auto_20231026_1334'),
    ]

    operations = [
        migrations.AddField(
            model_name='poll',
            name='vote_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
