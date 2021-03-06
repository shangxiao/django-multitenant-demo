# Generated by Django 3.2.7 on 2021-09-03 17:46

import app.models.models
import app.models.users
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('is_superuser', models.BooleanField(default=False)),
                ('is_staff', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('objects', app.models.users.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Level',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Tenant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='AdminUser',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='app.user')),
                ('is_superuser_adminuser', models.BooleanField(default=True, editable=False)),
            ],
            options={
                'abstract': False,
            },
            bases=('app.user',),
            managers=[
                ('objects', app.models.users.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='ContractorUser',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='app.user')),
            ],
            options={
                'abstract': False,
            },
            bases=('app.user',),
            managers=[
                ('objects', app.models.users.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('level', app.models.models.TenantForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.level')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.tenant')),
            ],
            options={
                'abstract': False,
                'unique_together': {('id', 'tenant_id')},
            },
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.tenant')),
            ],
            options={
                'abstract': False,
                'unique_together': {('id', 'tenant_id')},
            },
        ),
        migrations.AddField(
            model_name='level',
            name='site',
            field=app.models.models.TenantForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.site'),
        ),
        migrations.AddField(
            model_name='level',
            name='tenant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.tenant'),
        ),
        migrations.CreateModel(
            name='VendorUser',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='app.user')),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.vendor')),
            ],
            options={
                'abstract': False,
            },
            bases=('app.user',),
            managers=[
                ('objects', app.models.users.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='TenantUser',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='app.user')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.tenant')),
            ],
            options={
                'abstract': False,
            },
            bases=('app.user',),
            managers=[
                ('objects', app.models.users.UserManager()),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='level',
            unique_together={('id', 'tenant_id')},
        ),
    ]
