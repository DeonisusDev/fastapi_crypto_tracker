from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.routes import health, prices
from app.db.database import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(health.router)
app.include_router(prices.router)


