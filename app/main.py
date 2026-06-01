from fastapi import FastAPI
from app.api.routes import health, prices

app = FastAPI()
app.include_router(health.router)
app.include_router(prices.router)


