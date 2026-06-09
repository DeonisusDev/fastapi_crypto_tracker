from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.routes import health, prices
from app.db.database import create_tables
from app.scheduler.jobs import update_top_coins
import logging

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()
scheduler.add_job(update_top_coins, "interval", minutes=1, next_run_time=datetime.now())


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan function to handle startup and shutdown events for the FastAPI application.
    This function is responsible for creating the database tables and starting the scheduler when the application starts,
    and shutting down the scheduler when the application stops.
    """
    logger.info("Creating tables...")
    
    await create_tables()
    logger.info("Tables created!")

    scheduler.start()
    logger.info("Scheduler started!")
    
    yield
    scheduler.shutdown()
    logger.info("Scheduler shutdown complete.")


app = FastAPI(lifespan=lifespan)
app.include_router(health.router)
app.include_router(prices.router)


