# Generated by Django 3.1 on 2021-09-07 21:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_auto_20210906_1503'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='company',
            field=models.CharField(blank=True, default='', max_length=300),
        ),
        migrations.AddField(
            model_name='profile',
            name='job',
            field=models.CharField(blank=True, default='', max_length=300),
        ),
    ]
