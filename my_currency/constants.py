class Currencies:
    USD = 'USD'
    EUR = 'EUR'
    GBP = 'GBP'
    CHF = 'CHF'
    
    @classmethod
    def values(cls):
        return [cls.USD, cls.EUR, cls.GBP, cls.CHF]
