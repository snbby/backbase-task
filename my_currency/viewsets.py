from threading import Thread

from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet

from my_currency.controllers import CurrencyExchangeController
from my_currency.exceptions import NoProviderException
from my_currency.models import Currency, Provider
from my_currency.serializers import (ConvertAmountRequestSerializer,
                                     ConvertAmountResponseSerializer,
                                     CurrenciesV1ModelSerializer,
                                     CurrenciesV2ModelSerializer,
                                     CurrencyRatesRequestSerializer,
                                     CurrencyRatesResponseSerializer,
                                     ErrorResponseSerializer,
                                     ProviderModelSerializer)
from my_currency.utils import fill_historical_data


class CurrencyRatesViewSet(ViewSet):
    def list(self, request):
        currency_rates_serializer = CurrencyRatesRequestSerializer(data=request.query_params)
        currency_rates_serializer.is_valid(raise_exception=True)
        filters = currency_rates_serializer.validated_data

        currency_controller = CurrencyExchangeController()
        try:
            rates = currency_controller.currency_rates_list(
                source_currency=filters['source_currency'],
                date_from=filters['date_from'],
                date_to=filters['date_to']
            )
            serializer = CurrencyRatesResponseSerializer(rates)
            return Response(serializer.data)
        except NoProviderException as e:
            serializer = ErrorResponseSerializer(data={'message': str(e)})
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data, status=400)

        
class ConvertAmountViewSet(ViewSet):
    def list(self, request):
        convert_amount_serializer = ConvertAmountRequestSerializer(data=request.query_params)
        convert_amount_serializer.is_valid(raise_exception=True)
        filters = convert_amount_serializer.validated_data

        currency_controller = CurrencyExchangeController()
        try:
            rate = currency_controller.convert_amount(
                source_currency=filters['source_currency'],
                exchanged_currency=filters['exchanged_currency'],
                amount=filters['amount'],
            )
            serializer = ConvertAmountResponseSerializer(rate)
            return Response(serializer.data)
        except NoProviderException as e:
            serializer = ErrorResponseSerializer(data={'message': str(e)})
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data, status=400)


class ProvidersModelviewSet(ModelViewSet):
    queryset = Provider.objects.all()
    serializer_class = ProviderModelSerializer


class CurrenciesV1ModelViewSet(ModelViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrenciesV1ModelSerializer

class CurrenciesV2ModelViewSet(ModelViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrenciesV2ModelSerializer


class LaunchAsyncHistoryTask(ViewSet):
    def create(self, request):
        currency_rates_serializer = CurrencyRatesRequestSerializer(data=request.data)
        currency_rates_serializer.is_valid(raise_exception=True)
        data = currency_rates_serializer.validated_data
        Thread(target=fill_historical_data, args=(data['date_from'], data['date_to'], data['source_currency'])).start()
        return Response({'message': 'Task launched successfully'})
