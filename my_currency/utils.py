import datetime
from threading import Thread

from django.db import IntegrityError

from my_currency import logger
from my_currency.controllers import CurrencyExchangeController
from my_currency.currency_clients import currency_beacon_client
from my_currency.models import Currency, Provider


def fill_currencies():
    logger.info('Inserting currencies into db...')
    currencies = [
        {'code': 'USD', 'name': 'United States Dollar', 'symbol': '$'},
        {'code': 'EUR', 'name': 'Euro', 'symbol': '€'},
        {'code': 'GBP', 'name': 'British Pound Sterling', 'symbol': '£'},
        {'code': 'CHF', 'name': 'Swiss Franc', 'symbol': 'CHF'},
    ]

    for currency in currencies:
        try:
            Currency.objects.create(
                code=currency['code'],
                name=currency['name'],
                symbol=currency['symbol'],
            )
            logger.info(f'Currency {currency["name"]} inserted to db.')
        except IntegrityError:
            logger.error(f'Failed to save currency {currency["name"]}. Looks like it already exists.')

def fill_providers():
    logger.info('Inserting providers into db...')
    for num, provider in enumerate(Provider.ProviderNames.choices):
        try:
            Provider.objects.create(
                name=provider[0],
                priority=num+1,
                is_active=True,
            )
            logger.info(f'Provider {provider[0]} inserted to db.')
        except IntegrityError:
            logger.error(f'Failed to save provider {provider[0]}. Looks like it already exists.')

def fill_date_range(date_from: datetime.date, date_to: datetime.date, source_currency: str):
    logger.info(f'Loading historical data: {date_from} → {date_to}')
    controller = CurrencyExchangeController()
    rates = currency_beacon_client.timeseries(
        base_currency=source_currency,
        start_date=date_from,
        end_date=date_to,
    )
    currency_beacon_provider = Provider.objects.get(name=Provider.ProviderNames.CURRENCY_BEACON.value)
    controller.save_rates_to_db(rates, source_currency, currency_beacon_provider.id)

def fill_historical_data(date_from: datetime.date, date_to: datetime.date, source_currency: str):
    logger.info(
        f'Launching threads to fetch historical data '
        f'from {date_from} to {date_to}, source_currency: {source_currency}...'
    )
    for chunk_start, chunk_end in month_chunks(date_from, date_to):
        Thread(target=fill_date_range, args=(chunk_start, chunk_end, source_currency)).start()
    logger.info('All threads launched.')


def month_chunks(start_date: datetime.date, end_date: datetime.date):
    current = start_date
    while current < end_date:
        next_month = current + datetime.timedelta(days=30)
        yield (current, min(next_month, end_date))
        current = next_month
