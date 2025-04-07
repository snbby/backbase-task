from django.db import models


class Provider(models.Model):
    class ProviderNames(models.TextChoices):
        CURRENCY_BEACON = 'currency_beacon', 'Currency Beacon'
        MOCK = 'mock', 'Mock'

    name = models.CharField(choices=ProviderNames.choices, max_length=20, unique=True)
    description = models.TextField(null=True, blank=True, max_length=200)
    priority = models.PositiveIntegerField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=20, db_index=True)
    symbol = models.CharField(max_length=10)

    def __str__(self):
        return self.code

class CurrencyExchangeRate(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['provider', 'source_currency', 'exchanged_currency', 'valuation_date'],
                name='unique_main'
            )
        ]
    provider = models.ForeignKey(Provider, related_name='exchanges', on_delete=models.CASCADE)
    source_currency = models.ForeignKey(Currency, related_name='exchanges', on_delete=models.CASCADE)
    exchanged_currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    valuation_date = models.DateField(db_index=True)
    rate_value = models.DecimalField(db_index=True, decimal_places=6, max_digits=18)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.source_currency} to {self.exchanged_currency} on {self.valuation_date}'
    
class ExchangeCurrency(models.Model):
    provider = models.ForeignKey(Provider, related_name='exchange_currencies', on_delete=models.CASCADE)
    source_currency = models.ForeignKey(Currency, related_name='exchange_currencies', on_delete=models.CASCADE)
    exchanged_currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    source_amount = models.DecimalField(decimal_places=6, max_digits=18)
    exchanged_amount = models.DecimalField(decimal_places=6, max_digits=18)
    rate_value = models.DecimalField(decimal_places=6, max_digits=18)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.source_amount} {self.source_currency} to {self.exchanged_currency} '
