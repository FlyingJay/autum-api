# Generated by Django 3.1 on 2021-11-29 05:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0039_signup_school'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='height_max',
            field=models.IntegerField(blank=True, default=100, help_text='Height (inches)', null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='height_min',
            field=models.IntegerField(blank=True, default=0, help_text='Height (inches)', null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='show_height_cm',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='profile',
            name='distance_max',
            field=models.IntegerField(blank=True, default=25),
        ),
    ]
