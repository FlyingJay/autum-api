# Generated by Django 3.1 on 2021-09-28 19:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0030_remove_profile_school'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='school',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.school'),
        ),
    ]
