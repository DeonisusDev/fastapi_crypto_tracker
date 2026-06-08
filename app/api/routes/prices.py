from fastapi import APIRouter, Depends, HTTPException, Path, Query
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.models.coin import Coin
from sqlalchemy import select
from app.schemas.price import PriceResponse, PricesHistory, PriceRecord
from app.services.cache import get_cached_price, set_cache
 
router = APIRouter()


@router.get("/price/{coin_id}")
async def get_price(
    coin_id: str = Path(..., description="The name of the coin for which to get the price (e.g., bitcoin)", max_length=50, pattern=r"^[a-z0-9-]+$"),
    db: AsyncSession = Depends(get_db)
):
    """
    Fetches the current price of a cryptocurrency from CoinGecko API, with caching and error handling.
    
    Args:
        coin_id: The name of the coin (e.g., 'bitcoin')
        db: Database session for storing price history
    
    Returns:
        PriceResponse: The current price of the coin in USD
    
    Raises:
        HTTPException: If the coin is not found, external API is unavailable, or other errors occur
    """

    cached_price = get_cached_price(coin_id)
    if cached_price is not None:
        return PriceResponse(coin_id=coin_id, price_usd=cached_price)
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params={"ids": coin_id, "vs_currencies": "usd"})
            data = response.json()
            if coin_id in data:
                price = data[coin_id]["usd"]
                set_cache(coin_id, price)
                db.add(Coin(coin_id=coin_id, price_usd=price))
                await db.commit()
                return PriceResponse(
                    coin_id=coin_id,
                    price_usd=price
                )
            raise HTTPException(status_code=404, detail=f"Coin '{coin_id}' not found")
    except httpx.ConnectTimeout:
        raise HTTPException(status_code=503, detail="External API is unavailable")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Error from external API: {e.response.text}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/history/{coin_id}")
async def get_price_history(
    coin_id: str = Path(..., description="The name of the coin for which to get the price history (e.g., bitcoin)", max_length=50, pattern=r"^[a-z0-9-]+$"),
    limit: int = Query(100, description="Maximum number of price records to return", ge=1, le=1000),
    offset: int = Query(0, description="Number of records to skip for pagination", ge=0),
    db: AsyncSession = Depends(get_db)
):
    """
    Fetches the price history of a cryptocurrency from the database.
    
    Args:
        coin_id: The name of the coin for which to get the price history (e.g., 'bitcoin')
        db: Database session for querying price history
    
    Returns:
        PricesHistory: The price history of the coin
    
    Raises:
        HTTPException: If no price history is found for the specified coin
    """

    result = await db.execute(
        select(Coin.current_price_usd, Coin.timestamp).where(Coin.coin_id == coin_id).order_by(Coin.timestamp.desc()).limit(limit).offset(offset)
    )
    rows = result.fetchall()
    if not rows:
        raise HTTPException(status_code=404, detail=f"No price history found for '{coin_id}'")
    
    prices = [PriceRecord(price_usd=row.current_price_usd, timestamp=row.timestamp) for row in rows]
    return PricesHistory(coin_id=coin_id, prices=prices)