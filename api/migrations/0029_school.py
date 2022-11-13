# Generated by Django 3.1 on 2021-09-28 19:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0028_auto_20210921_1539'),
    ]

    operations = [
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200)),
                ('country', models.CharField(max_length=200)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
