# Generated by Django 4.2.16 on 2024-11-27 17:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('joblist', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='jobapply',
            name='jobfield',
        ),
        migrations.AddField(
            model_name='joblisting',
            name='jobfield',
            field=models.CharField(blank=True, choices=[('arts', 'arts'), ('business', 'business'), ('communications', 'communications'), ('education', 'education'), ('healthcare', 'healthcare'), ('hospitality', 'hospitality'), ('information technology', 'information technology'), ('law enforcement', 'law enforcement'), ('sales and marketing', 'sales and marketing'), ('science', 'science'), ('transportation', 'transportation'), ('other', 'other')], default='other', max_length=100, null=True),
        ),
    ]
