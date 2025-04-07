import factory
from faker import Faker

from my_currency.models import Currency, CurrencyExchangeRate, Provider

fake = Faker()

class CurrencyExchangeRateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CurrencyExchangeRate

    provider = factory.Iterator(Provider.objects.filter(name=Provider.ProviderNames.CURRENCY_BEACON.value))
    source_currency = factory.Iterator(Currency.objects.all())
    exchanged_currency = factory.Iterator(Currency.objects.all())
    valuation_date = factory.Faker('date')
    rate_value = factory.Faker('random_number', digits=5, fix_len=True)
    created_at = factory.Faker('date_time')
    updated_at = factory.Faker('date_time')
