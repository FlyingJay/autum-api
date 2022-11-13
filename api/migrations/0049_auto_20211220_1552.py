# Generated by Django 3.1 on 2021-12-20 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0048_profile_importance_experiences'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='importance_experiences',
            field=models.IntegerField(blank=True, choices=[(0, 'NONE'), (1, 'LEAST'), (2, 'SOMEWHAT'), (3, 'VERY')], default=0, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='importance_interests',
            field=models.IntegerField(blank=True, choices=[(0, 'NONE'), (1, 'LEAST'), (2, 'SOMEWHAT'), (3, 'VERY')], default=0, null=True),
        ),
    ]
