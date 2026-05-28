from datetime import datetime
from fastapi import Depends, FastAPI, HTTPException, Path
import httpx
from pydantic import BaseModel
import time
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models import Coin
from sqlalchemy import select
import logging


app = FastAPI()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


class PriceResponse(BaseModel):
    coin_id: str
    price_usd: float


class PriceRecord(BaseModel):
    price_usd: float
    timestamp: datetime


class PricesHistory(BaseModel):
    coin_id: str
    prices: list[PriceRecord]


cache = {}
CACHE_EXPIRATION = 60  # Cache expiration time in seconds

def get_cached_price(coin_id: str):
    if coin_id in cache:
        price, cached_at = cache[coin_id]
        if time.time() - cached_at < CACHE_EXPIRATION:
            logger.info(f"Cache hit for {coin_id}")
            logger.info(f"Cached price: {price} USD")
            logger.info(f"Cached at: {time.ctime(cached_at)}")
            return price
    return None


def set_cache(coin_id: str, price: float):
    cache[coin_id] = (price, time.time())


@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/price/{coin_id}")
async def get_price(
    coin_id: str = Path(..., description="The name of the coin for which to get the price (e.g., bitcoin)", max_length=50, pattern=r"^[a-z0-9-]+$"),
    db: AsyncSession = Depends(get_db)
):

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


@app.get("/history/{coin_id}")
async def get_price_history(
    coin_id: str = Path(..., description="The name of the coin for which to get the price history (e.g., bitcoin)", max_length=50, pattern=r"^[a-z0-9-]+$"),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Coin.price_usd, Coin.timestamp).where(Coin.coin_id == coin_id).order_by(Coin.timestamp.desc())
    )
    rows = result.fetchall()
    if not rows:
        raise HTTPException(status_code=404, detail=f"No price history found for '{coin_id}'")
    
    prices = [PriceRecord(price_usd=row.price_usd, timestamp=row.timestamp) for row in rows]
    return PricesHistory(coin_id=coin_id, prices=prices)