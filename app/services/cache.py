import time
import logging

cache = {}
CACHE_EXPIRATION = 60  # Cache expiration time in seconds

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


def get_cached_price(coin_id: str):
    """
    Returns cached price for a coin if it exists and hasn't expired.
    
    Args:
        coin_id: The coin identifier (e.g., 'bitcoin')
    
    Returns:
        Cached price as float, or None if not found or expired.
    """

    if coin_id in cache:
        price, cached_at = cache[coin_id]
        if time.time() - cached_at < CACHE_EXPIRATION:
            logger.info(f"Cache hit for {coin_id}")
            logger.info(f"Cached price: {price} USD")
            logger.info(f"Cached at: {time.ctime(cached_at)}")
            return price
    return None


def set_cache(coin_id: str, price: float):
    """
    Sets the cache for a coin with the current price and timestamp.
    
    Args:
        coin_id: The coin identifier (e.g., 'bitcoin')
        price: The price to cache
    """

    cache[coin_id] = (price, time.time())
