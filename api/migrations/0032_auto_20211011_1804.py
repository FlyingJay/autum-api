# Generated by Django 3.1 on 2021-10-11 18:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0031_profile_school'),
    ]

    operations = [
        migrations.AddField(
            model_name='like',
            name='is_ended',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='like',
            name='is_ended_reason',
            field=models.IntegerField(blank=True, choices=[(0, 'NO_CHEMISRY'), (1, 'UNRESPONSIVE'), (2, 'SOMEONE_ELSE')], null=True),
        ),
    ]
