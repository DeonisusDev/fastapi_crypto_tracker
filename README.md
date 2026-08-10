# Crypto Market Data Platform

A backend service for collecting, storing, and exposing cryptocurrency market data from CoinGecko.

The service automatically collects top 10 cryptocurrencies by market cap every minute and provides REST API endpoints for accessing current prices and historical data.

## Features

- 🔄 **Automated Data Collection**: Scheduled job fetches top coins every minute
- 💾 **Persistent Storage**: PostgreSQL database stores historical price data
- ⚡ **Performance**: In-memory cache (60 sec TTL) reduces external API calls
- 🚀 **Async**: Built with async/await for high performance
- 🐳 **Containerized**: Docker Compose setup for local development
- 📊 **Clean Architecture**: Separated layers (API, ETL, Database, Scheduler)

## Technology Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy (async)
- **HTTP Client**: httpx (async)
- **Scheduling**: APScheduler
- **Caching**: In-memory dict
- **Container**: Docker & Docker Compose

## API Endpoints

- `GET /` — Health check status
- `GET /price/{coin_id}` — Get current price for a coin
  - Example: `GET /price/bitcoin`
  - Returns: `{"coin_id": "bitcoin", "price_usd": 68000.50}`
  - Uses cache when available, fetches fresh data if needed

## Getting Started

### Prerequisites
- Python 3.9+
- Docker & Docker Compose
- Git

### Local Development Setup

1. **Clone repository**
```bash
git clone <repo>
cd crypto_tracker
```

2. **Create and activate virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup environment variables**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

5. **Start PostgreSQL**
```bash
docker compose up -d
```

6. **Run the application**
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## Testing

Run the test suite:
```bash
pytest tests/
pytest tests/ -v  # verbose output
```

## Project Structure

```
app/
├── main.py              # FastAPI app entry point
├── api/routes/          # API endpoints
├── etl/                 # Extract, Transform, Load pipeline
├── models/              # SQLAlchemy ORM models
├── db/                  # Database configuration
├── scheduler/           # Scheduled jobs
├── services/            # Business logic (cache, etc.)
└── schemas/             # Pydantic response models

tests/                   # Test suite
docker-compose.yml       # PostgreSQL setup
requirements.txt         # Python dependencies
```

## How It Works

### Scheduled Ingestion
Every minute, a background job:
1. Fetches top 10 coins from CoinGecko API
2. Transforms the data into database models
3. Stores prices in PostgreSQL
4. Logs the operation

### On-Demand Price Request
When you request `/price/{coin_id}`:
1. Checks in-memory cache first
2. If cached (within 60 sec), returns immediately
3. If not cached, fetches from CoinGecko
4. Stores in database and cache
5. Returns the price

## Documentation

See [docs/architecture.md](docs/architecture.md) for detailed architecture documentation.

## Future Enhancements

- [ ] Historical price queries with date ranges
- [ ] Multiple data providers support
- [ ] Analytics endpoints (moving averages, top movers)
- [ ] Redis cache for distributed deployments
- [ ] Database migrations with Alembic
- [ ] Prometheus metrics and monitoring
- [ ] Web dashboard UI



