# Generated by Django 3.1 on 2021-10-27 14:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0036_auto_20211026_0219'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='gradient',
            field=models.CharField(blank=True, default='Orchid', max_length=20),
        ),
    ]