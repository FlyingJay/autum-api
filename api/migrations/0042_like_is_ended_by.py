# Generated by Django 3.1 on 2021-11-29 22:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0041_auto_20211129_2233'),
    ]

    operations = [
        migrations.AddField(
            model_name='like',
            name='is_ended_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ended_conversations', to=settings.AUTH_USER_MODEL),
        ),
    ]
