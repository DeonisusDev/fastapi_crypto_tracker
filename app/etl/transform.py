from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator
import logging

logger = logging.getLogger(__name__)


class CoinData(BaseModel):
    """
    A Pydantic model representing the transformed data for a cryptocurrency coin.
    This model is used to validate and structure the data fetched from the CoinGecko API before it is loaded into the database.
    
     Attributes:
        coin_id: The unique identifier of the coin (e.g., 'bitcoin')
        coin_symbol: The symbol of the coin (e.g., 'btc')
        coin_name: The full name of the coin (e.g., 'Bitcoin')
        current_price_usd: The current price of the coin in USD
        market_cap: The market capitalization of the coin in USD
        market_cap_rank: The rank of the coin based on market capitalization
        total_volume: The total trading volume of the coin in the last 24 hours in USD
        price_change_percentage_24h: The percentage change in price over the last 24 hours
        last_updated: The timestamp of the last update for the coin data
    """
    model_config = ConfigDict(populate_by_name=True)

    coin_id: str = Field(alias="id")
    coin_symbol: str = Field(alias="symbol")
    coin_name: str = Field(alias="name")
    current_price_usd: float = Field(alias="current_price")
    market_cap: float = Field(alias="market_cap")
    market_cap_rank: int = Field(alias="market_cap_rank")
    total_volume: float = Field(alias="total_volume")
    price_change_percentage_24h: float = Field(default=0.0)
    last_updated: datetime = Field(alias="last_updated")

    @field_validator("price_change_percentage_24h", mode="before")
    @classmethod
    def default_zero(cls, v):
        """Ensures that if the price change percentage is missing or None, it defaults to 0.0."""
        return v if v is not None else 0.0
    

def transform_coins(raw_coins: list[dict]) -> list[CoinData]:
    """
    Transforms a list of raw coin data dictionaries into a list of CoinData objects.
    This function validates the raw data against the CoinData model and logs any validation errors.
    If a coin's data fails validation, it is skipped and a warning is logged.
    
    Args:
        raw_coins: A list of dictionaries containing raw coin data fetched from the API
    Returns:
        A list of CoinData objects that have been successfully validated and transformed from the raw data
    """
    result = []
    for coin in raw_coins:
        try:
            result.append(CoinData.model_validate(coin))
        except Exception as e:
            logger.warning(f"Skipping coin due to validation error: {e}")
    return result