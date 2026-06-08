from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.routes import health, prices
from app.db.database import create_tables
import logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Creating tables...")
    await create_tables()
    logger.info("Tables created!")
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(health.router)
app.include_router(prices.router)


