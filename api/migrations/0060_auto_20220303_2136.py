# Generated by Django 3.1 on 2022-03-03 21:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0059_auto_20220303_1643'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ambassador',
            options={'ordering': ['first_name']},
        ),
    ]
