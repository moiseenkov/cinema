# Generated by Django 2.2.7 on 2019-11-28 06:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0011_ticket'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ticket',
            name='paid',
        ),
        migrations.AddField(
            model_name='ticket',
            name='receipt',
            field=models.CharField(blank=True, max_length=36),
        ),
    ]
