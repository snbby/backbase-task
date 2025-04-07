import json
import os

import pytest
from django.conf import settings
from rest_framework.test import APIClient

from my_currency.tests.factories import CurrencyExchangeRateFactory
from my_currency.utils import fill_currencies, fill_providers


@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def fill_initial_data(db):
    fill_currencies()
    fill_providers()

@pytest.fixture
def currency_beacon_timeseries_response():
    fixture_path = os.path.join(settings.BASE_DIR, 'my_currency', 'tests', 'fixtures', 'timeseries.json')
    with open(fixture_path) as f:
        return json.load(f)
    
@pytest.fixture
def currency_beacon_latest_response():
    fixture_path = os.path.join(settings.BASE_DIR, 'my_currency', 'tests', 'fixtures', 'latest.json')
    with open(fixture_path) as f:
        return json.load(f)
    
@pytest.fixture
def currency_exchange():
    return CurrencyExchangeRateFactory()

@pytest.fixture
def currency_exchanges():
    return CurrencyExchangeRateFactory.create_batch(10)
