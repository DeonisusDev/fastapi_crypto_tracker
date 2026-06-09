# Crypto Market Data Platform Architecture

## Project Goal

This project is a backend service for collecting, storing, and exposing
cryptocurrency market data from CoinGecko.

The current implementation provides:

- async Python with FastAPI
- PostgreSQL database with SQLAlchemy async ORM
- ETL pipeline for data ingestion
- scheduled data collection every minute
- RESTful API endpoints for price data
- in-memory caching for performance
- Docker-based local development

The project demonstrates practical backend engineering skills:

- async/await patterns in Python
- FastAPI framework and routing
- SQLAlchemy ORM with async support
- PostgreSQL data modeling
- External API integration (CoinGecko)
- APScheduler for scheduled tasks
- error handling and logging
- Docker Compose setup

## Target Users

The primary users are:

- developers who need an API for cryptocurrency price data
- analysts who want historical market data
- evaluators assessing backend engineering capabilities

## Current Architecture

### Technology Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy with async support
- **Async Client**: httpx
- **Scheduling**: APScheduler (AsyncIOScheduler)
- **Caching**: In-memory (dict-based)
- **External API**: CoinGecko

### Database Model

The current implementation uses a simplified single-table schema:

#### coins

Stores cryptocurrency data and prices.

Columns:

- `id` (Primary Key): Unique identifier
- `coin_id` (String): Unique coin identifier from CoinGecko (e.g., 'bitcoin')
- `coin_symbol` (String): Coin symbol (e.g., 'btc')
- `coin_name` (String): Full name (e.g., 'Bitcoin')
- `current_price_usd` (Numeric): Current price in USD
- `market_cap` (Numeric): Market capitalization in USD
- `market_cap_rank` (Integer): Ranking by market cap
- `total_volume` (Numeric): 24-hour trading volume in USD
- `price_change_percentage_24h` (Numeric): 24-hour price change percentage
- `timestamp` (DateTime): When the record was created
- `last_updated` (DateTime): When the coin data was last updated

## Application Layers

The application is organized into clear, separated layers:

### API Layer (`app/api/routes/`)

Handles HTTP requests and responses.

Current endpoints:

- `health.py`: Health check endpoint at `/`
- `prices.py`: Price endpoints
  - `GET /price/{coin_id}`: Get current price for a coin

Responsibilities:

- validates path and query parameters
- caches results when available
- calls ETL functions to fetch and update data
- returns Pydantic response models
- handles HTTP errors and exceptions

### Database Layer (`app/db/`)

Manages database connectivity and session management.

- `database.py`: 
  - Creates async engine with PostgreSQL
  - Provides async session factory
  - Implements `get_db()` dependency for FastAPI
  - Creates tables on startup

### Models Layer (`app/models/`)

Defines SQLAlchemy ORM models.

- `coin.py`: `Coin` model representing the `coins` table
  - Uses SQLAlchemy async ORM with mapped columns
  - Includes all cryptocurrency data fields

### ETL Layer (`app/etl/`)

Handles data extraction, transformation, and loading.

- `extract.py`:
  - `fetch_coin()`: Fetches data for a single coin via CoinGecko API
  - `fetch_top_coins()`: Fetches top 10 coins by market cap
  - Uses httpx for async HTTP requests
  - Includes search functionality with best-match logic

- `transform.py`:
  - `transform_coins()`: Converts CoinGecko API responses into `Coin` ORM objects
  - Normalizes data structures

- `load.py`:
  - `load_coins_to_db()`: Inserts or updates coins in the database
  - Handles database operations

### Scheduler Layer (`app/scheduler/`)

Manages scheduled tasks using APScheduler.

- `jobs.py`:
  - `update_top_coins()`: Scheduled job that runs every 1 minute
  - Fetches top coins, transforms data, and loads into database
  - Includes error logging and handling

### Services Layer (`app/services/`)

Provides application services.

- `cache.py`:
  - In-memory cache for price data
  - `get_cached_price()`: Retrieves cached price
  - `set_cache()`: Stores price in cache
  - Reduces API calls to external services

### Schemas Layer (`app/schemas/`)

Defines Pydantic models for API responses.

- `price.py`: Response schemas
  - `PriceResponse`: Single price response
  - `PricesHistory`: Historical price data
  - `PriceRecord`: Individual price record

## Current API Endpoints

### Health

```
GET /
```

Returns a status indicator that the application is running.

Response:
```json
{
  "status": "ok"
}
```

### Prices

```
GET /price/{coin_id}
```

Returns the current price for a cryptocurrency.

Parameters:
- `coin_id` (path): The coin identifier (e.g., 'bitcoin')

Response:
```json
{
  "coin_id": "bitcoin",
  "price_usd": 68000.50
}
```

Behavior:
- First checks in-memory cache
- If cached, returns immediately
- If not cached, fetches from CoinGecko API
- Stores result in database and cache
- Returns cached value on subsequent requests

## Data Flow

### Scheduled Ingestion (`update_top_coins`)

Runs every 1 minute via APScheduler:

1. Fetch top 10 coins from CoinGecko API using `fetch_top_coins()`
2. Transform API response into `Coin` ORM objects using `transform_coins()`
3. Load coins into PostgreSQL database using `load_coins_to_db()`
4. Log success or error

### On-Demand Price Request

When a client requests `/price/{coin_id}`:

1. Check in-memory cache for the price
2. If found in cache, return immediately
3. If not cached:
   - Fetch data from CoinGecko API using `fetch_coin()`
   - Transform into `Coin` object using `transform_coins()`
   - Load into database using `load_coins_to_db()`
   - Store price in cache
4. Return `PriceResponse` with the price

### Startup

When the application starts (lifespan startup):

1. Create all database tables based on SQLAlchemy models
2. Initialize APScheduler
3. Schedule `update_top_coins()` job
4. Start the scheduler
5. FastAPI app is ready to accept requests

### Shutdown

When the application stops (lifespan shutdown):

1. Shutdown the scheduler
2. Close database connections

## Error Handling

The application handles errors at multiple levels:

### API Layer

- Parameter validation using Pydantic
- HTTPException for API errors (e.g., 404 for unknown coins)
- Returns appropriate HTTP status codes

### ETL Layer

- Logs errors during fetch, transform, and load operations
- Gracefully handles API timeouts and failures
- Continues execution when errors occur in scheduled jobs

### Scheduler

- Catches exceptions in scheduled tasks
- Logs errors for debugging
- Continues running even if individual tasks fail

## Observability

The project includes basic observability:

- **Logging**: Structured logging at key points
  - Database creation on startup
  - Scheduled job execution
  - API requests and responses
  - Errors during ETL operations
  - Coin data loading status

- **Health Check**: `/` endpoint for basic liveness check

- **Database Records**: Coins table provides audit trail of what data was fetched

## Testing

Current test coverage:

- `test_cache.py`: Tests in-memory cache functionality
  - Cache storage and retrieval
  - Cache behavior

Tests can be run with pytest:

```bash
pytest tests/
```

## Local Development

### Setup with Docker Compose

The project includes Docker Compose configuration for PostgreSQL:

```bash
docker compose up
```

This starts:
- PostgreSQL database on port 5432

### Running the Application

```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables (.env file)
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/crypto_tracker

# Run with uvicorn
uvicorn app.main:app --reload
```

The application will be available at `http://localhost:8000`

### Environment Variables

Create a `.env` file with:

```
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/crypto_tracker
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=crypto_tracker
```

## Project Structure

```
app/
├── __init__.py
├── main.py                    # FastAPI app setup, lifespan, routes
├── api/
│   ├── __init__.py
│   └── routes/
│       ├── __init__.py
│       ├── health.py         # Health check endpoint
│       └── prices.py         # Price endpoints
├── core/
│   ├── __init__.py
│   └── config.py             # Configuration management
├── db/
│   ├── __init__.py
│   └── database.py           # Database setup, session management
├── models/
│   ├── __init__.py
│   └── coin.py               # SQLAlchemy Coin model
├── etl/
│   ├── __init__.py
│   ├── extract.py            # CoinGecko API client
│   ├── transform.py          # Data transformation
│   └── load.py               # Database loading
├── scheduler/
│   ├── __init__.py
│   └── jobs.py               # Scheduled tasks
├── services/
│   ├── __init__.py
│   └── cache.py              # In-memory caching
└── schemas/
    ├── __init__.py
    └── price.py              # Pydantic response models

tests/
├── __init__.py
└── test_cache.py             # Cache tests

docker-compose.yml            # PostgreSQL setup
Dockerfile                     # Application container
requirements.txt              # Python dependencies
README.md                      # Project documentation
```

## Future Enhancements

Possible improvements for future versions:

### Data Model
- Separate `assets` and `price_ticks` tables for historical data
- `ingestion_runs` table to track data collection jobs
- Indexes on frequently queried columns

### API Endpoints
- `/assets`: List all tracked assets
- `/prices/{coin_id}/latest`: Get latest price
- `/prices/{coin_id}/history`: Get historical prices with pagination
- `/analytics/top-movers`: Find coins with largest price changes
- `/ingestion/runs`: View ingestion run history

### Infrastructure
- Redis cache instead of in-memory
- Celery or Arq for background job processing
- Prometheus metrics and monitoring
- Database migrations with Alembic

### Features
- Support for additional data providers
- Analytics and calculations (moving averages)
- CSV/Parquet export functionality
- Web dashboard UI
- Rate limiting and authentication

### Quality
- Comprehensive test suite
- Database migration strategy
- Linting and formatting (Black, Ruff)
- Integration tests
- Load testing
