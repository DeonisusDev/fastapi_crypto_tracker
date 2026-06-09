from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
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
        coin_data = [coin.model_dump() for coin in coins]

        stmt = insert(Coin).values(coin_data).on_conflict_do_nothing(
            index_elements=["coin_id", "last_updated"]
            )
        await db.execute(stmt)
        await db.commit()
        logger.info(f"Successfully loaded {len(coins)} coins into the database")
    except Exception as e:
        logger.error(f"Error occurred while loading coins into the database: {e}")
        raise