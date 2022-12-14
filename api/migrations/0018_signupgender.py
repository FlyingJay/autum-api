# Generated by Django 3.1 on 2021-09-19 03:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0017_auto_20210919_0300'),
    ]

    operations = [
        migrations.CreateModel(
            name='SignupGender',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('gender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='signups', to='api.gender')),
                ('signup', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='genders', to='api.signup')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
