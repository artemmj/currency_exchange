# Generated by Django 3.0.3 on 2020-02-20 14:09

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0010_auto_20200214_0219'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='HistoryExchanges',
            new_name='HistoryExchange',
        ),
        migrations.RenameModel(
            old_name='USDRelations',
            new_name='USDRelation',
        ),
    ]