# Generated by Django 3.1 on 2022-03-21 22:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0064_autumphone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='autumphone',
            name='config',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='autum_phones', to='api.autumconfig'),
        ),
    ]
