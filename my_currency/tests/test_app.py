import pytest
from django.urls import reverse
from rest_framework import status

from my_currency.exceptions import NoProviderException
from my_currency.models import CurrencyExchangeRate, Provider


@pytest.mark.django_db
def test_get_currency_rates_no_providers(api_client):
    # We need to fill initial data to have providers
    url = reverse('currency-rates-list') 
    params = {
        'source_currency': 'USD',
        'date_from': '2023-10-01',
        'date_to': '2023-10-02'
    }
    response = api_client.get(url, params)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['message'] == NoProviderException.default_message

@pytest.mark.django_db
def test_get_currency_rates_incorrect_label(api_client, fill_initial_data):
    url = reverse('currency-rates-list')
    params = {
        'source_currency': 'INCORRECT_CURRENCY',  # Invalid input here
        'date_from': '2023-10-01',
        'date_to': '2023-10-02'
    }
    response = api_client.get(url, params)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['source_currency'][0].code == 'invalid_choice'

@pytest.mark.django_db
def test_get_currency_rates_incorrect_date(api_client, fill_initial_data):
    url = reverse('currency-rates-list')
    params = {
        'source_currency': 'USD',
        'date_from': '2023-10-42',  # Invalid input here
        'date_to': '2023-10-02'
    }
    response = api_client.get(url, params)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data.get('date_from') is not None

@pytest.mark.django_db
def test_get_currency_rates_incorrect_date_from(api_client, fill_initial_data):
    url = reverse('currency-rates-list')
    params = {
        'source_currency': 'USD',
        'date_from': '2023-10-03',  # Invalid input here
        'date_to': '2023-10-02'
    }
    response = api_client.get(url, params)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data.get('date_from') is not None

@pytest.mark.django_db
def test_get_currency_mock_currency_beacon(api_client, mocker, currency_beacon_timeseries_response, fill_initial_data):
    # Mocking the response from the currency beacon client from the fixture
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = currency_beacon_timeseries_response
    mocker.patch('my_currency.currency_clients.requests.get', return_value=mock_response)

    url = reverse('currency-rates-list')
    params = {
        'source_currency': 'USD',
        'date_from': '2023-10-01',
        'date_to': '2023-12-31'
    }
    response = api_client.get(url, params)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['provider_name'] == Provider.ProviderNames.CURRENCY_BEACON.value
    assert len(response.data['data']) == 92

@pytest.mark.django_db
def test_get_currency_lower_currency_beacon_priority(api_client, fill_initial_data):
    # Switching lower priority for currency beacon provider
    url = reverse('providers-detail', args=[1])
    response = api_client.patch(url, {'priority': 99})
    assert response.status_code == status.HTTP_200_OK


    url = reverse('currency-rates-list')
    params = {
        'source_currency': 'USD',
        'date_from': '2023-10-01',
        'date_to': '2023-10-02'
    }
    response = api_client.get(url, params)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['provider_name'] == Provider.ProviderNames.MOCK.value
    assert len(response.data['data']) == 2

def test_get_currency_rates_currency_beacon_400(api_client, mocker, fill_initial_data):
    # Mocking 400 response from the currency beacon client, expecting results from the mock client
    mock_response = mocker.Mock()
    mock_response.status_code = 400
    mock_response.json.return_value = {'error': 'Bad Request'}
    mocker.patch('my_currency.currency_clients.requests.get', return_value=mock_response)

    url = reverse('currency-rates-list')
    params = {
        'source_currency': 'USD',
        'date_from': '2023-10-01',
        'date_to': '2023-10-02'
    }
    response = api_client.get(url, params)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['provider_name'] == Provider.ProviderNames.MOCK.value


@pytest.mark.django_db
def test_switch_off_currency_beacon_provider(api_client, fill_initial_data):
    # Switching off currency beacon provider
    url = reverse('providers-detail', args=[1])
    response = api_client.patch(url, {'is_active': False})
    assert response.status_code == status.HTTP_200_OK

    url = reverse('currency-rates-list') 
    params = {
        'source_currency': 'USD',
        'date_from': '2023-10-01',
        'date_to': '2023-10-02'
    }
    response = api_client.get(url, params)
    assert response.data['provider_name'] == Provider.ProviderNames.MOCK.value
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_switch_off_all_providers(api_client, fill_initial_data):
    # Switching off currency beacon provider
    url = reverse('providers-detail', args=[1])
    response = api_client.patch(url, {'is_active': False})
    assert response.status_code == status.HTTP_200_OK

    # Switching off Mock provider
    url = reverse('providers-detail', args=[2])
    response = api_client.patch(url, {'is_active': False})
    assert response.status_code == status.HTTP_200_OK

    url = reverse('currency-rates-list') 
    params = {
        'source_currency': 'USD',
        'date_from': '2023-10-01',
        'date_to': '2023-10-02'
    }
    response = api_client.get(url, params)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['message'] == NoProviderException.default_message

@pytest.mark.django_db
def test_convert_amount_mocked_currency_beacon(api_client, mocker, currency_beacon_latest_response, fill_initial_data):
    # Mocking the response from the currency beacon client from fixture
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = currency_beacon_latest_response
    mocker.patch('my_currency.currency_clients.requests.get', return_value=mock_response)

    url = reverse('convert-amount-list')
    params = {
        'source_currency': 'USD',
        'exchanged_currency': 'EUR',
        'amount': 50
    }
    response = api_client.get(url, params)
    assert response.status_code == status.HTTP_200_OK
    assert response.data.get('provider_name') == Provider.ProviderNames.CURRENCY_BEACON.value
    assert response.data.get('exchanged_amount') is not None
    assert response.data.get('rate_value') is not None

@pytest.mark.django_db
def test_convert_amount_mocked_client(api_client, mocker, fill_initial_data):
    # Switching off currency beacon provider, checking that we recieve mock response
    url = reverse('providers-detail', args=[1])
    response = api_client.patch(url, {'is_active': False})
    assert response.status_code == status.HTTP_200_OK

    url = reverse('convert-amount-list')
    params = {
        'source_currency': 'USD',
        'exchanged_currency': 'EUR',
        'amount': 50
    }
    response = api_client.get(url, params)
    assert response.status_code == status.HTTP_200_OK
    assert response.data.get('provider_name') == Provider.ProviderNames.MOCK.value
    assert response.data.get('exchanged_amount') is not None
    assert response.data.get('rate_value') is not None

@pytest.mark.django_db
def test_fill_db_with_fake_currency_exchanges(api_client, fill_initial_data, currency_exchanges):
    # Test faker and factory for dummy data
    assert len(currency_exchanges) == CurrencyExchangeRate.objects.all().count()

@pytest.mark.django_db
def test_currencies_v1_crud(api_client, fill_initial_data):
    # List
    url = reverse('currencies-v1-list')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 4
    first_currency = response.data[0]['id']

    # Retrieve
    url = reverse('currencies-v1-detail', args=(first_currency,))
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['id'] == first_currency

    # Patch
    url = reverse('currencies-v1-detail', args=(first_currency,))
    payload = {
        'code': 'Cod',
        'name': 'Some name',
        'symbol': 'Symb'
    }
    response = api_client.patch(url, payload)
    assert response.data['id'] == first_currency
    assert response.status_code == status.HTTP_200_OK

    # Delete
    url = reverse('currencies-v1-detail', args=(first_currency,))
    response = api_client.delete(url, payload)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Check deletion
    url = reverse('currencies-v1-list')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 3

    # Create
    url = reverse('currencies-v1-list')
    payload = {
        'code': 'USD',
        'name': 'United States Dollar',
        'symbol': '$'
    }
    response = api_client.post(url, payload)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['code'] == payload['code']
