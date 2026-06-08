import httpx
import logging

logger = logging.getLogger(__name__)

async def fetch_top_coins() -> list[dict]:
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            return data
    except httpx.ConnectTimeout:
        logger.error("External API is unavailable")
        return []
    except httpx.HTTPStatusError as e:
        logger.error(f"Error from external API: {e.response.text}")
        return []
    except Exception as e:
        logger.error(f"Internal server error: {str(e)}")
        return []
