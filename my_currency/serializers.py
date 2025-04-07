from rest_framework import serializers

from my_currency.constants import Currencies
from my_currency.models import Currency, Provider


class CurrencyRatesRequestSerializer(serializers.Serializer):
    source_currency = serializers.ChoiceField(choices=Currencies.values(), required=True)
    date_from = serializers.DateField(required=True, input_formats=['%Y-%m-%d'])
    date_to = serializers.DateField(required=True, input_formats=['%Y-%m-%d'])

    def validate(self, data):
        if data['date_from'] > data['date_to']:
            raise serializers.ValidationError({'date_from': 'date_from must be before end date_to.'})
        return data


class CurrencyRatesResponseSerializer(serializers.Serializer):
    provider_name = serializers.CharField()
    date_from = serializers.DateField()
    date_to = serializers.DateField()
    source_currency = serializers.CharField()
    data = serializers.DictField()

class ConvertAmountRequestSerializer(serializers.Serializer):
    amount = serializers.FloatField(required=True)
    source_currency = serializers.ChoiceField(choices=Currencies.values(), required=True)
    exchanged_currency = serializers.ChoiceField(choices=Currencies.values(), required=True)

class ConvertAmountResponseSerializer(serializers.Serializer):
    provider_name = serializers.CharField()
    source_currency = serializers.ChoiceField(choices=Currencies.values())
    exchanged_currency = serializers.ChoiceField(choices=Currencies.values())
    source_amount = serializers.FloatField()
    exchanged_amount = serializers.FloatField()
    rate_value = serializers.FloatField()

class ErrorResponseSerializer(serializers.Serializer):
    message = serializers.CharField()


class CurrenciesV1ModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = '__all__'

class CurrenciesV2ModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = '__all__'

class ProviderModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = '__all__'
