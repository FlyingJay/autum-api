# Generated by Django 3.1 on 2022-02-22 15:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0056_auto_20220222_1513'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='gender',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='like',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='signup',
            options={'ordering': ['-id']},
        ),
        migrations.DeleteModel(
            name='Message',
        ),
    ]