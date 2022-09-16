# Generated by Django 3.2.15 on 2022-09-16 09:01

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='OemofData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='OemofScalar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_node', models.CharField(max_length=255)),
                ('to_node', models.CharField(max_length=255)),
                ('attribute', models.CharField(max_length=255)),
                ('value', models.CharField(max_length=255)),
                ('type', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='OemofSequence',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_node', models.CharField(max_length=255)),
                ('to_node', models.CharField(max_length=255, null=True)),
                ('attribute', models.CharField(max_length=255)),
                ('value', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(), size=None)),
                ('type', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='OemofDataset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('input', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='data_input', to='django_oemof.oemofdata')),
                ('result', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='data_result', to='django_oemof.oemofdata')),
            ],
        ),
        migrations.AddField(
            model_name='oemofdata',
            name='scalars',
            field=models.ManyToManyField(to='django_oemof.OemofScalar'),
        ),
        migrations.AddField(
            model_name='oemofdata',
            name='sequences',
            field=models.ManyToManyField(to='django_oemof.OemofSequence'),
        ),
    ]
