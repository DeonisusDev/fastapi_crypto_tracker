from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.etl.transform import CoinData
from app.models.coin import Coin
import logging

logger = logging.getLogger(__name__)


async def load_coins_to_db(coins: List[CoinData], 
                           db: AsyncSession):
    """
    Loads a list of CoinData objects into the database as Coin records.
    
    Args:
    - coins: A list of CoinData objects to be loaded into the database
    - db: An active AsyncSession for database operations
    
    Raises:
    - Exception: If any error occurs during the database insertion process
    """
    try:
        for coin in coins:
            db.add(Coin(
                coin_id=coin.coin_id,
                coin_symbol=coin.coin_symbol,
                coin_name=coin.coin_name,
                current_price_usd=coin.current_price_usd,
                market_cap=coin.market_cap,
                market_cap_rank=coin.market_cap_rank,
                total_volume=coin.total_volume,
                price_change_percentage_24h=coin.price_change_percentage_24h,
                last_updated=coin.last_updated
            ))
        await db.commit()
        logger.info(f"Successfully loaded {len(coins)} coins into the database")
    except Exception as e:
        logger.error(f"Error occurred while loading coins into the database: {e}")
        raise