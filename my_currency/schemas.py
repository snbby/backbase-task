from pydantic import BaseModel


class Meta(BaseModel):
    code: int
    disclaimer: str


class Rates(BaseModel):
    CHF: float
    EUR: float
    GBP: float
    USD: float


class LatestResponseData(BaseModel):
    base: str
    date: str
    rates: Rates


class LatestResponse(BaseModel):
    base: str
    date: str
    meta: Meta
    rates: Rates
    response: LatestResponseData

class HistoricalResponse(LatestResponse):
    pass

class TimeseriesResponse(BaseModel):
    meta: Meta
    response: dict[str, Rates]

class Currency(BaseModel):
    code: str
    decimal_mark: str
    id: int
    name: str
    precision: int
    short_code: str
    subunit: int
    symbol: str
    symbol_first: bool
    thousands_separator: str


class CurrenciesResponse(BaseModel):
    meta: Meta
    response: list[Currency]
