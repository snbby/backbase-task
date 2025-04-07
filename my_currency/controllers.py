from collections import defaultdict
from datetime import datetime

from my_currency import logger
from my_currency.constants import Currencies
from my_currency.currency_clients import (currency_beacon_client,
                                          mocked_currency_client)
from my_currency.exceptions import CurrencyBeaconException, NoProviderException
from my_currency.models import Currency, CurrencyExchangeRate, Provider
from my_currency.schemas import Rates


class CurrencyExchangeController:
    def __init__(self):
        self.providers = self._get_providers()

    def _prepare_currency_rates_response_from_db(
            self, source_currency: str, date_from: datetime.date, date_to: datetime.date, 
            rates: list[CurrencyExchangeRate], provider_name: str
            ) -> dict:
        logger.info('Preparing response obj from DB objects...')
        rates_data = defaultdict(dict)
        for rate in rates:
            rates_data[rate.valuation_date][rate.exchanged_currency.code] = rate.rate_value

        output = {
            'provider_name': provider_name,
            'source_currency': source_currency,
            'date_from': date_from,
            'date_to': date_to,
            'data': rates_data
        }
        return output
    
    def _prepare_currency_rates_response_from_provider(
            self, source_currency: str, date_from: datetime.date, date_to: datetime.date, 
            rates: dict[str, Rates], provider_name: str
            ) -> dict:
        logger.info('Preparing response obj from provider...')
        rates_data = defaultdict(dict)
        for day, rate in rates.items():
            for currency_code, rate_value in rate.model_dump().items():
                rates_data[day][currency_code] = rate_value

        output = {
            'provider_name': provider_name,
            'source_currency': source_currency,
            'date_from': date_from,
            'date_to': date_to,
            'data': rates_data,
        }
        return output

    def _get_rates_from_db(
            self, source_currency: str, date_from: datetime.date, date_to: datetime.date
            ) -> list[CurrencyExchangeRate]:
        logger.info('Fetching rates from DB...')
        rates = CurrencyExchangeRate.objects.select_related('source_currency', 'exchanged_currency').filter(
            source_currency__code=source_currency,
            valuation_date__range=[date_from, date_to]
        )
        return rates

    def save_rates_to_db(self, rates: list[Rates], source_currency: str, provider_id: int) -> None:
        logger.info(f'Saving rates to DB for {source_currency}')
        currencies = Currency.objects.all()
        currencies_dict = {currency.code: currency.id for currency in currencies}

        rate_objects = []
        for day, rate in rates.items():
            for exchanged_currency, rate_value in rate.model_dump().items():
                if exchanged_currency in currencies_dict:
                    rate_objects.append(
                        CurrencyExchangeRate(
                            provider_id=provider_id,
                            source_currency_id=currencies_dict.get(source_currency),
                            exchanged_currency_id=currencies_dict.get(exchanged_currency),
                            valuation_date=day,
                            rate_value=rate_value
                        )
                    )

        CurrencyExchangeRate.objects.bulk_create(
            rate_objects, update_conflicts=True, 
            unique_fields=['provider', 'source_currency', 'exchanged_currency', 'valuation_date'],
            update_fields=['rate_value'],
        )
        logger.info(f'Rates saved to DB for {source_currency}')
                    
    def currency_rates_list(self, source_currency: str, date_from: datetime.date, date_to: datetime.date) -> dict:
        logger.info(f'Fetching rates for {source_currency} from {date_from} to {date_to}')
        expected_number_of_rates = self._get_expected_number_of_rates(date_from, date_to)
        rates = self._get_rates_from_db(source_currency, date_from, date_to)
        num_rates = len(rates)
        if num_rates == expected_number_of_rates:
            logger.info(f'Expected: {expected_number_of_rates}, got: all.')
            response_rates = self._prepare_currency_rates_response_from_db(
                source_currency=source_currency,
                date_from=date_from,
                date_to=date_to,
                rates=rates,
                provider_name='DB'
            )
        else:
            logger.info(f'Expected: {expected_number_of_rates}, got: {num_rates}. Fetching from provider...')
            while True:
                try:
                    provider = next(self.providers)
                except StopIteration:
                    logger.error(NoProviderException.default_message)
                    raise NoProviderException()
                
                try:
                    rates = provider['client'].timeseries(
                        base_currency=source_currency,
                        start_date=date_from,
                        end_date=date_to
                    )
                    break
                except CurrencyBeaconException:
                    logger.error(f'Error fetching rates from {provider["client"].provider_name}')
            if provider['client'].provider_name == Provider.ProviderNames.CURRENCY_BEACON.value:
                self.save_rates_to_db(rates, source_currency, provider['id'])
            response_rates = self._prepare_currency_rates_response_from_provider(
                source_currency=source_currency,
                date_from=date_from,
                date_to=date_to,
                rates=rates,
                provider_name=provider['client'].provider_name
            )
        return response_rates
    

    def convert_amount(self, source_currency: str, exchanged_currency: str, amount: float) -> float:
        logger.info(f'Converting {amount} from {source_currency} to {exchanged_currency}')
        while True:
            try:
                provider = next(self.providers)
            except StopIteration:
                logger.error(NoProviderException.default_message)
                raise NoProviderException()
            rates = provider['client'].latest(base_currency=source_currency)
            if rates:
                break
        response = {
            'provider_name': provider['client'].provider_name,
            'source_currency': source_currency,
            'exchanged_currency': exchanged_currency,
            'source_amount': float(amount),
            'exchanged_amount': float(amount) * getattr(rates, exchanged_currency),
            'rate_value': getattr(rates, exchanged_currency),
        }

        return response

    def _get_providers(self):
        PROVIDER_MAP = {
            Provider.ProviderNames.CURRENCY_BEACON.value: currency_beacon_client,
            Provider.ProviderNames.MOCK.value: mocked_currency_client,
        }
        providers_obj = list(Provider.objects.filter(is_active=True).order_by('priority'))
        provider_clients = [{'id': provider.id, 'client': PROVIDER_MAP[provider.name]} for provider in providers_obj]
        for provider in provider_clients:
            logger.info(f'Checking provider {provider["client"].provider_name}...')
            yield provider
    
    def _get_expected_number_of_rates(self, date_from: datetime.date, date_to: datetime.date) -> int:
        days_diff = (date_to - date_from).days
        return (days_diff + 1) * len(Currencies.values())

    def get_exchange_rate_data(
            source_currency: str, exchanged_currency: str, valuation_date: str, provider: str
            ) -> float:
        """
        Supposed to be signature from the task, but I wasn't sure where did you want to use it.
        Since provider is chosen in the controller, and provider options are not visible in the viewset I changed it
        """
        pass
