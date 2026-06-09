import httpx
import logging

logger = logging.getLogger(__name__)

async def search_coin(query: str) -> list[dict]:
    """
    Search for a coin by name or symbol using CoinGecko API.
    Tries to find the best match based on symbol, name, or id.

    Args:
        query: The search query (coin name or symbol)

    Returns:
        A list of coin data dictionaries matching the search query, or an empty list if no matches
    
    Raises:
        Exception: If any error occurs during the API request or processing
    """
    try:
        # First, search for the coin
        search_url = "https://api.coingecko.com/api/v3/search?query=" + query
        async with httpx.AsyncClient() as client:
            response = await client.get(search_url)
            response.raise_for_status()
            search_data = response.json()
            
            if search_data.get("coins") and len(search_data["coins"]) > 0:
                coins_list = search_data["coins"]
                
                # Try to find best match by symbol or name
                best_match = None
                query_lower = query.lower()
                
                # First priority: exact symbol match
                for coin in coins_list:
                    if coin.get("symbol", "").lower() == query_lower:
                        best_match = coin
                        break
                
                # Second priority: name starts with query
                if not best_match:
                    for coin in coins_list:
                        if coin.get("name", "").lower().startswith(query_lower):
                            best_match = coin
                            break
                
                # Third priority: id contains query
                if not best_match:
                    for coin in coins_list:
                        if query_lower in coin.get("id", "").lower():
                            best_match = coin
                            break
                
                # Fallback to first result
                if not best_match:
                    best_match = coins_list[0]
                
                coin_id = best_match["id"]
                logger.info(f"Found coin '{query}' -> ID: {coin_id} ({best_match['name']})")
                
                # Now fetch the market data for this coin
                markets_url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={coin_id}"
                response = await client.get(markets_url)
                response.raise_for_status()
                return response.json()
            return []
    except httpx.ConnectTimeout:
        logger.error(f"Timeout searching for coin: {query}")
        return []
    except httpx.HTTPStatusError as e:
        logger.error(f"Error searching for coin '{query}': {e.response.text}")
        return []
    except Exception as e:
        logger.error(f"Error searching for coin '{query}': {str(e)}")
        return []

async def fetch_top_coins() -> list[dict]:
    """
    Fetches the top 10 coins by market cap from CoinGecko API.
    
    Returns:
        A list of dictionaries containing data for the top 10 coins, or an empty list if an error occurs
    
    Raises:
        Exception: If any error occurs during the API request or processing
    """
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


async def fetch_coin(coin_id: str) -> list[dict] | None:
    """
    Fetches data for a specific coin by its ID from CoinGecko API.
    If the coin is not found, it tries to search for it by name or symbol.

    Args:
        coin_id: The ID of the coin to fetch (e.g., 'bitcoin')
    
    Returns:
        A list of dictionaries containing data for the coin, or None if not found or an error
    
    Raises:
        Exception: If any error occurs during the API request or processing
    """
    try:
        url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={coin_id}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            
            # If no results, try to search for the coin
            if not data or len(data) == 0:
                logger.info(f"Direct lookup failed for '{coin_id}', trying search...")
                data = await search_coin(coin_id)
            
            return data
    except httpx.ConnectTimeout:
        logger.error("External API is unavailable")
        return None
    except httpx.HTTPStatusError as e:
        logger.error(f"Error from external API: {e.response.text}")
        return None
    except Exception as e:
        logger.error(f"Internal server error: {str(e)}")
        return None