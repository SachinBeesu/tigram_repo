# Generated by Django 3.1.7 on 2021-07-28 03:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_app', '0048_applicationform_approved_by_division'),
    ]

    operations = [
        migrations.AddField(
            model_name='applicationform',
            name='destination_state',
            field=models.CharField(default='', max_length=500),
        ),
    ]
