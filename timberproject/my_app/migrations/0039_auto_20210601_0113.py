# Generated by Django 3.1.7 on 2021-05-31 19:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_app', '0038_auto_20210530_1300'),
    ]

    operations = [
        migrations.AddField(
            model_name='division',
            name='is_delete',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='range',
            name='is_delete',
            field=models.BooleanField(default=False),
        ),
    ]
