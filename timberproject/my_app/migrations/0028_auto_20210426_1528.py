# Generated by Django 3.1.7 on 2021-04-26 09:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_app', '0027_auto_20210426_1523'),
    ]

    operations = [
        migrations.AddField(
            model_name='applicationform',
            name='tp_expiry_date',
            field=models.DateField(default='2021-03-19'),
        ),
        migrations.AddField(
            model_name='applicationform',
            name='tp_expiry_status',
            field=models.BooleanField(default=False),
        ),
    ]
