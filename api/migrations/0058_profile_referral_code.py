# Generated by Django 3.1 on 2022-03-03 14:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0057_auto_20220222_1517'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='referral_code',
            field=models.CharField(blank=True, default=None, max_length=255, null=True),
        ),
    ]
