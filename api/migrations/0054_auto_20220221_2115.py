# Generated by Django 3.1 on 2022-02-21 21:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0053_auto_20220217_1852'),
    ]

    operations = [
        migrations.AlterField(
            model_name='like',
            name='is_ended_reason',
            field=models.IntegerField(blank=True, choices=[(1, 'NO_CHEMISRY'), (2, 'UNRESPONSIVE'), (3, 'SOMEONE_ELSE'), (4, 'ACCIDENT'), (101, 'REPORT_PHOTOS'), (102, 'REPORT_SPAM'), (103, 'REPORT_HARASSMENT'), (501, 'ACCOUNT_DELETED')], null=True),
        ),
    ]
