import datetime
import random

from django.conf import settings
import requests

from my_currency import logger
from my_currency.constants import Currencies
from my_currency.exceptions import CurrencyBeaconException
from my_currency.models import Provider
from my_currency.schemas import (CurrenciesResponse, Currency,
                                 HistoricalResponse, LatestResponse, Rates,
                                 TimeseriesResponse)


class BaseCurrencyClient:
    def __init__(self):
        self.symbols = Currencies.values()
        self.symbols_str = ','.join(self.symbols)
        self.date_format = '%Y-%m-%d'

    def latest(self, base_currency: str) -> dict:
        raise NotImplementedError('Subclasses should implement this!')
    
    def historical(self, base_currency: str, date: str) -> dict:
        raise NotImplementedError('Subclasses should implement this!')

class MockedCurrencyClient(BaseCurrencyClient):
    provider_name = Provider.ProviderNames.MOCK.value
   
    def _generate_rates(self, base_currency: str) -> Rates:
        return Rates(
            CHF=round(random.uniform(0.9, 1.1), 6) if base_currency != Currencies.CHF else 1.0,
            EUR=round(random.uniform(0.9, 1.1), 6) if base_currency != Currencies.EUR else 1.0,
            GBP=round(random.uniform(0.9, 1.1), 6) if base_currency != Currencies.GBP else 1.0,
            USD=round(random.uniform(0.9, 1.1), 6) if base_currency != Currencies.USD else 1.0
        )

    def latest(self, base_currency: str) -> Rates:
        return self._generate_rates(base_currency)

    def historical(self, base_currency: str, date: str) -> Rates:
        return self._generate_rates(base_currency)

    def timeseries(self, base_currency: str, start_date: datetime.date, end_date: datetime.date) -> dict[str, Rates]:
        rates = {}
        current_date = start_date
        while current_date <= end_date:
            rates[current_date.strftime(self.date_format)] = self._generate_rates(base_currency)
            current_date = current_date + datetime.timedelta(days=1)
        return rates

class CurrencyBeaconClient(BaseCurrencyClient):
    api_key = settings.CURRENCY_BEACON_API_KEY
    base_url = 'https://api.currencybeacon.com/v1'
    provider_name = Provider.ProviderNames.CURRENCY_BEACON.value

    def latest(self, base_currency: str) -> Rates:
        url = f'{self.base_url}/latest'
        params = {
            'api_key': self.api_key,
            'base': base_currency,
            'symbols': self.symbols_str,
        }
        response = requests.get(url, params=params)
        response = self._handle_response(response)
        validated_response = LatestResponse(**response.json())
        return validated_response.rates

    def historical(self, base_currency: str, date: str) -> Rates:
        url = f'{self.base_url}/historical'
        params = {
            'api_key': self.api_key,
            'base': base_currency,
            'symbols': self.symbols_str,
            'date': date,
        }
        response = requests.get(url, params=params)
        response = self._handle_response(response)
        validated_response = HistoricalResponse(**response.json())
        return validated_response.rates
        
    def currencies(self) -> list[Currency]:
        url = f'{self.base_url}/currencies'
        params = {
            'api_key': self.api_key,
            'type': 'fiat'
        }
        response = requests.get(url, params=params)
        response = self._handle_response(response)
        validated_response = CurrenciesResponse(**response.json())
        return validated_response.response
    
    def timeseries(self, base_currency: str, start_date: datetime.date, end_date: datetime.date) -> dict[str, Rates]:
        url = f'{self.base_url}/timeseries'
        params = {
            'api_key': self.api_key,
            'base': base_currency,
            'symbols': self.symbols_str,
            'start_date': start_date.strftime(self.date_format),
            'end_date': end_date.strftime(self.date_format),
        }
        response = requests.get(url, params=params)
        response = self._handle_response(response)
        validated_response = TimeseriesResponse(**response.json())
        return validated_response.response
    
    def _handle_response(self, response: requests.Response) -> requests.Response:
        if response.status_code == 200:
            return response
        else:
            logger.warning(f'Received error from Currency Beacon API: {response.status_code}, {response.text}')
            raise CurrencyBeaconException(f'Error: {response.status_code}, {response.text}')


currency_beacon_client = CurrencyBeaconClient()
mocked_currency_client = MockedCurrencyClient()
