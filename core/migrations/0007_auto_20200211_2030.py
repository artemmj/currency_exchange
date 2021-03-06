# Generated by Django 3.0.3 on 2020-02-11 17:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20200211_2014'),
    ]

    operations = [
        migrations.RenameField(
            model_name='usdrelations',
            old_name='GPB',
            new_name='GBP',
        ),
        migrations.AlterField(
            model_name='historyexchanges',
            name='transfer_currency',
            field=models.CharField(choices=[('EUR', 'EUR'), ('USD', 'USD'), ('GBP', 'GBP'), ('RUB', 'RUB'), ('BTC', 'BTC')], max_length=3),
        ),
        migrations.AlterField(
            model_name='user',
            name='currency',
            field=models.CharField(choices=[('EUR', 'EUR'), ('USD', 'USD'), ('GBP', 'GBP'), ('RUB', 'RUB'), ('BTC', 'BTC')], default='BTC', max_length=3),
        ),
    ]
