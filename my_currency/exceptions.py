class NoProviderException(Exception):
    default_message = 'No providers available, please define providers in the DB.'

    def __init__(self, message: str = default_message):
        super().__init__(message)

class CurrencyBeaconException(Exception):
    pass
