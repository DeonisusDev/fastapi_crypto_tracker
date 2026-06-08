from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator
import logging

logger = logging.getLogger(__name__)


class CoinData(BaseModel):
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
        return v if v is not None else 0.0
    

def transform_coins(raw_coins: list[dict]) -> list[CoinData]:
    result = []
    for coin in raw_coins:
        try:
            result.append(CoinData.model_validate(coin))
        except Exception as e:
            logger.warning(f"Skipping coin due to validation error: {e}")
    return result