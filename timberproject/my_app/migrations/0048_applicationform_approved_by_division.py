# Generated by Django 3.1.7 on 2021-07-27 06:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('my_app', '0047_auto_20210727_0617'),
    ]

    operations = [
        migrations.AddField(
            model_name='applicationform',
            name='approved_by_division',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='applicationform_approved_by_division', to=settings.AUTH_USER_MODEL),
        ),
    ]
