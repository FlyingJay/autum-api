# Generated by Django 3.1 on 2021-11-29 22:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0040_auto_20211129_0557'),
    ]

    operations = [
        migrations.AlterField(
            model_name='like',
            name='is_ended_reason',
            field=models.IntegerField(blank=True, choices=[(0, 'NO_CHEMISRY'), (1, 'UNRESPONSIVE'), (2, 'SOMEONE_ELSE'), (3, 'ACCIDENT'), (100, 'REPORT_PHOTOS'), (101, 'REPORT_SPAM'), (102, 'REPORT_HARASSMENT')], null=True),
        ),
    ]
