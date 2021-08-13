# Generated by Django 3.1.7 on 2021-04-20 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_app', '0020_auto_20210416_1101'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='photo_proof_img',
            field=models.CharField(default='static/images/no_image.png', max_length=255),
        ),
        migrations.AlterField(
            model_name='image_documents',
            name='aadhar_detail',
            field=models.CharField(default='static/images/no_image.png', max_length=200),
        ),
        migrations.AlterField(
            model_name='image_documents',
            name='declaration',
            field=models.CharField(default='static/images/no_image.png', max_length=200),
        ),
        migrations.AlterField(
            model_name='image_documents',
            name='location_sktech',
            field=models.CharField(default='static/images/no_image.png', max_length=200),
        ),
        migrations.AlterField(
            model_name='image_documents',
            name='revenue_application',
            field=models.CharField(default='static/images/no_image.png', max_length=200),
        ),
        migrations.AlterField(
            model_name='image_documents',
            name='revenue_approval',
            field=models.CharField(default='static/images/no_image.png', max_length=200),
        ),
        migrations.AlterField(
            model_name='image_documents',
            name='signature_img',
            field=models.CharField(default='static/images/no_image.png', max_length=200),
        ),
        migrations.AlterField(
            model_name='image_documents',
            name='tree_ownership_detail',
            field=models.CharField(default='static/images/no_image.png', max_length=200),
        ),
    ]
