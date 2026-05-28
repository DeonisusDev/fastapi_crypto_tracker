from datetime import datetime
from pydantic import BaseModel


class PriceResponse(BaseModel):
    """
    Response model for the current price of a cryptocurrency.
    """
    
    coin_id: str
    price_usd: float


class PriceRecord(BaseModel):
    """
    Model for a single price record.
    """

    price_usd: float
    timestamp: datetime


class PricesHistory(BaseModel):
    """
    Response model for the price history of a cryptocurrency.
    """
    
    coin_id: str
    prices: list[PriceRecord]