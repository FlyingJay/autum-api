# Generated by Django 3.1 on 2022-01-03 15:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0049_auto_20211220_1552'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='firebase_token',
            field=models.CharField(blank=True, default=None, max_length=255, null=True),
        ),
    ]