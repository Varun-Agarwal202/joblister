# Generated by Django 5.1.4 on 2025-02-03 18:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('joblist', '0005_meetingevent'),
    ]

    operations = [
        migrations.AddField(
            model_name='meetingevent',
            name='current_people',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='meetingevent',
            name='limit_people',
            field=models.IntegerField(default=30),
        ),
        migrations.AddField(
            model_name='meetingevent',
            name='private',
            field=models.BooleanField(default=False),
        ),
    ]
