from app.db.database import SessionLocal
from app.etl.extract import fetch_top_coins
from app.etl.load import load_coins_to_db
from app.etl.transform import transform_coins
import logging

logger = logging.getLogger(__name__)


async def update_top_coins():
    """
    Fetches top 10 coins by market cap and updates the database
    
    This function is intended to be run as a scheduled job to keep the database updated with the latest top coins.
    It fetches the top coins from the CoinGecko API, transforms the raw data into CoinData objects, and then loads them into the database.
    If any errors occur during the process, they are logged for debugging purposes.
    
    Raises:
        Exception: If any error occurs during the fetching, transforming, or loading of coin data
    """
    try:
        top_coins = await fetch_top_coins()
        if top_coins:
            coins = transform_coins(top_coins)
            async with SessionLocal() as db:
                await load_coins_to_db(coins, db)
                logger.info(f"Updated top coins in the database: {len(coins)} coins")
        else:
            logger.warning("No top coins data fetched to update the database")
    except Exception as e:
        logger.error(f"Error updating top coins in the database: {str(e)}")