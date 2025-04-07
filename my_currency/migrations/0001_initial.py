# Generated by Django 5.2 on 2025-04-07 09:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=3, unique=True)),
                ('name', models.CharField(db_index=True, max_length=20)),
                ('symbol', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Provider',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('currency_beacon', 'Currency Beacon'), ('mock', 'Mock')], max_length=20, unique=True)),
                ('description', models.TextField(blank=True, max_length=200, null=True)),
                ('priority', models.PositiveIntegerField(unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='ExchangeCurrency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source_amount', models.DecimalField(decimal_places=6, max_digits=18)),
                ('exchanged_amount', models.DecimalField(decimal_places=6, max_digits=18)),
                ('rate_value', models.DecimalField(decimal_places=6, max_digits=18)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('exchanged_currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='my_currency.currency')),
                ('source_currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exchange_currencies', to='my_currency.currency')),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exchange_currencies', to='my_currency.provider')),
            ],
        ),
        migrations.CreateModel(
            name='CurrencyExchangeRate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valuation_date', models.DateField(db_index=True)),
                ('rate_value', models.DecimalField(db_index=True, decimal_places=6, max_digits=18)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('exchanged_currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='my_currency.currency')),
                ('source_currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exchanges', to='my_currency.currency')),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exchanges', to='my_currency.provider')),
            ],
            options={
                'constraints': [models.UniqueConstraint(fields=('provider', 'source_currency', 'exchanged_currency', 'valuation_date'), name='unique_main')],
            },
        ),
    ]
