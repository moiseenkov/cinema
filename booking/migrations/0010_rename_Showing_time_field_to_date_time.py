# Generated by Django 2.2.7 on 2019-11-18 10:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0009_setup_protected_on_delete_policty_for_Showming_fields'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='showing',
            options={'ordering': ['-date_time'], 'verbose_name': 'Showing', 'verbose_name_plural': 'Showings'},
        ),
        migrations.RenameField(
            model_name='showing',
            old_name='time',
            new_name='date_time',
        ),
        migrations.AlterUniqueTogether(
            name='showing',
            unique_together={('hall', 'movie', 'date_time')},
        ),
    ]
