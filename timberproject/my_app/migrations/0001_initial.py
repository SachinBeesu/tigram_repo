# Generated by Django 3.1.7 on 2021-03-15 11:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('phone', models.CharField(max_length=20, unique=True)),
                ('name', models.CharField(blank=True, max_length=50, null=True)),
                ('email', models.CharField(blank=True, max_length=50, null=True, unique=True)),
                ('signup_date', models.DateTimeField(auto_now_add=True)),
                ('login_date', models.DateTimeField()),
                ('login_status', models.CharField(default='', max_length=255)),
                ('user_status', models.CharField(default='', max_length=255)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Applicationform',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('address', models.CharField(blank=True, max_length=500, null=True)),
                ('survey_no', models.CharField(blank=True, max_length=50, null=True)),
                ('state', models.CharField(blank=True, default='', max_length=255)),
                ('district', models.CharField(blank=True, max_length=255)),
                ('taluka', models.CharField(blank=True, max_length=255)),
                ('block', models.CharField(blank=True, max_length=255)),
                ('proof_of_ownership_of_tree', models.CharField(blank=True, max_length=255)),
                ('village', models.CharField(default='', max_length=255)),
                ('species_of_trees', models.CharField(default='', max_length=255)),
                ('purpose', models.CharField(default='', max_length=255)),
                ('trees_proposed_to_cut', models.CharField(default='', max_length=255)),
                ('total_trees', models.CharField(default='', max_length=255)),
                ('destination_details', models.CharField(default='', max_length=500)),
                ('revenue_application', models.BooleanField(default=False)),
                ('location_sktech', models.BooleanField(default=False)),
                ('tree_ownership_detail', models.BooleanField(default=False)),
                ('aadhar_detail', models.BooleanField(default=False)),
                ('application_status', models.BooleanField(default=False)),
                ('verify_office', models.BooleanField(default=False)),
                ('reason_office', models.CharField(default='', max_length=500)),
                ('depty_range_officer', models.BooleanField(default=False)),
                ('reason_depty_ranger_office', models.CharField(default='', max_length=500)),
                ('verify_range_officer', models.BooleanField(default=False)),
                ('reason_range_officer', models.CharField(default='', max_length=500)),
                ('payment', models.CharField(default='', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Vehicle_detials',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vehicle_reg_no', models.CharField(blank=True, max_length=100, null=True)),
                ('driver_name', models.CharField(blank=True, max_length=200, null=True)),
                ('driver_phone', models.IntegerField(default=0)),
                ('mode_of_transport', models.CharField(blank=True, max_length=200, null=True)),
                ('license_image', models.CharField(blank=True, max_length=200, null=True)),
                ('photo_of_vehicle_with_number', models.CharField(blank=True, max_length=200, null=True)),
                ('app_form', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='app_vehicle', to='my_app.applicationform')),
            ],
        ),
        migrations.CreateModel(
            name='Timberlogdetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('species_of_tree', models.CharField(blank=True, max_length=100, null=True)),
                ('length', models.IntegerField(default=0)),
                ('breadth', models.IntegerField(default=0)),
                ('volume', models.IntegerField(default=0)),
                ('appform', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='app_id', to='my_app.applicationform')),
            ],
        ),
        migrations.CreateModel(
            name='RevenueOfficerdetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('post', models.CharField(blank=True, max_length=200, null=True, unique=True)),
                ('office_address', models.CharField(blank=True, max_length=500, null=True)),
                ('Rev_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rev_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='image_documents',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('revenue_approval', models.CharField(blank=True, max_length=200, null=True)),
                ('declaration', models.CharField(blank=True, max_length=200, null=True)),
                ('revenue_application', models.CharField(blank=True, max_length=200, null=True)),
                ('location_sktech', models.CharField(blank=True, max_length=200, null=True)),
                ('tree_ownership_detail', models.CharField(blank=True, max_length=200, null=True)),
                ('aadhar_detail', models.CharField(blank=True, max_length=200, null=True)),
                ('app_form', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='app_image', to='my_app.applicationform')),
            ],
        ),
        migrations.CreateModel(
            name='ForestOfficerdetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('post', models.CharField(blank=True, max_length=200, null=True, unique=True)),
                ('office_address', models.CharField(blank=True, max_length=500, null=True)),
                ('fod_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='fod_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
