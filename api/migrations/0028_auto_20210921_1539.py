# Generated by Django 3.1 on 2021-09-21 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0027_profile_is_archived'),
    ]

    operations = [
        migrations.RenameField(
            model_name='like',
            old_name='is_paid',
            new_name='is_liker_paid',
        ),
        migrations.AddField(
            model_name='like',
            name='is_subject_paid',
            field=models.BooleanField(default=False),
        ),
    ]