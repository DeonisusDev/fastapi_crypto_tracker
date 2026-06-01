# Crypto Price Tracker

FastAPI service for getting current cryptocurrency prices via CoinGecko API.

## Live Demo
https://fastapicryptotracker-production.up.railway.app

## Stack
- FastAPI
- PostgreSQL (price history)
- In-memory cache (60 sec TTL, reduces API load)
- Docker

## Endpoints
- `GET /` — health check
- `GET /price/{coin_id}` — current coin price
- `GET /history/{coin_id}` — price history from DB

## Setup

1. Clone the repository
2. Copy `.env.example` to `.env` and fill with your values
3. Start Postgres:
```bash
docker compose up -d
```
4. Install dependencies and run:
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

