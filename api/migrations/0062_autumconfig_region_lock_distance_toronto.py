# Generated by Django 3.1 on 2022-03-06 17:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0061_auto_20220306_1543'),
    ]

    operations = [
        migrations.AddField(
            model_name='autumconfig',
            name='region_lock_distance_toronto',
            field=models.IntegerField(default=42),
        ),
    ]
