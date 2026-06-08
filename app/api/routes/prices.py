from fastapi import APIRouter, Depends, HTTPException, Path, Query
import httpx
import logging
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.models.coin import Coin
from sqlalchemy import select
from app.schemas.price import PriceResponse, PricesHistory, PriceRecord
from app.services.cache import get_cached_price, set_cache
from app.etl.extract import fetch_coin

logger = logging.getLogger(__name__)
 
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
        fetch_result = await fetch_coin(coin_id)
        logger.info(f"Fetched data for {coin_id}: {fetch_result}")
        if fetch_result and len(fetch_result) > 0:
            coin_data = fetch_result[0]
            price = coin_data.get("current_price")
            if price is not None:
                set_cache(coin_id, price)
                last_updated = coin_data.get("last_updated")
                if last_updated is None:
                    last_updated = datetime.now(timezone.utc)
                elif isinstance(last_updated, str):
                    try:
                        # Parse ISO format datetime string
                        last_updated = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
                    except (ValueError, AttributeError):
                        last_updated = datetime.now(timezone.utc)
                logger.info(f"Adding coin to DB: {coin_id}")
                db.add(Coin(
                    coin_id=coin_id,
                    coin_symbol=coin_data.get("symbol", ""),
                    coin_name=coin_data.get("name", ""),
                    current_price_usd=price,
                    market_cap=coin_data.get("market_cap", 0),
                    market_cap_rank=coin_data.get("market_cap_rank", 0),
                    total_volume=coin_data.get("total_volume", 0),
                    price_change_percentage_24h=coin_data.get("price_change_percentage_24h", 0),
                    last_updated=last_updated
                ))
                logger.info(f"Committing transaction for {coin_id}")
                await db.commit()
                logger.info(f"Successfully saved {coin_id} to DB")
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