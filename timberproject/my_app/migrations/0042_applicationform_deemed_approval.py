# Generated by Django 3.1.7 on 2021-07-09 05:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_app', '0041_auto_20210709_1115'),
    ]

    operations = [
        migrations.AddField(
            model_name='applicationform',
            name='deemed_approval',
            field=models.BooleanField(default=False),
        ),
    ]
