# Generated by Django 5.1.4 on 2025-02-02 02:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('joblist', '0003_customuser_mentor'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='status_mentor',
            field=models.TextField(default='pending'),
        ),
    ]
