from django.contrib import admin

from my_currency import logger
from my_currency.controllers import CurrencyExchangeController
from my_currency.exceptions import NoProviderException
from my_currency.models import (Currency, CurrencyExchangeRate,
                                ExchangeCurrency, Provider)


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'priority', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'updated_at')
    ordering = ('priority',)

@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'name', 'symbol')
    ordering = ('id',)

@admin.register(CurrencyExchangeRate)
class CurrencyExchangeRateAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'provider', 'source_currency', 'exchanged_currency', 'valuation_date', 
        'rate_value', 'created_at', 'updated_at', 'provider'
        )
    list_filter = ('provider', 'source_currency')
    ordering = ('-created_at',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(ExchangeCurrency)
class ExchangeCurrencyAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'created_at', 'provider', 'source_currency', 'exchanged_currency', 
        'source_amount', 'exchanged_amount', 'rate_value', 'updated_at'
        )
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'provider', 'exchanged_amount', 'rate_value')

    def save_model(self, request, obj, form, change):
        logger.info(f'Converting {obj.source_amount} {obj.source_currency} to {obj.exchanged_currency}')
        currency_controller = CurrencyExchangeController()
        try:
            rate = currency_controller.convert_amount(
                source_currency=obj.source_currency.code,
                exchanged_currency=obj.exchanged_currency.code,
                amount=obj.source_amount,
            )
            self.message_user(
                request, 
                f'{obj.source_amount} {obj.source_currency} = {round(rate["exchanged_amount"], 2)} '
                f'{obj.exchanged_currency}. Rate: {rate["rate_value"]}', level='success'
                )

        except NoProviderException as e:
            self.message_user(request, f'Error: {str(e)}', level='error')
