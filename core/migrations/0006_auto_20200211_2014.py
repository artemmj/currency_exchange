# Generated by Django 3.0.3 on 2020-02-11 17:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20200207_1748'),
    ]

    operations = [
        migrations.RenameField(
            model_name='usdrelations',
            old_name='GBP',
            new_name='GPB',
        ),
    ]
