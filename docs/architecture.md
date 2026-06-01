# Crypto Market Data Platform Architecture

## Project Goal

This project is a backend service for collecting, storing, and exposing
cryptocurrency market data.

The current version can fetch the latest price for a coin from CoinGecko and
store the result in PostgreSQL. The target version should evolve into a small
data platform: it should ingest market data on a schedule, keep historical
records, expose clean API endpoints, and provide simple analytics.

The project is intended to demonstrate practical backend and data-engineering
skills:

- async Python and FastAPI
- PostgreSQL data modeling
- SQLAlchemy usage
- database migrations
- external API integration
- scheduled data ingestion
- error handling and observability
- testing
- Docker-based local development

## Target Users

The primary users are:

- developers who need an API for cryptocurrency price history
- analysts who want historical market data for selected coins
- hiring managers or interviewers evaluating backend/data-engineering skills

This is not meant to be a trading system. It does not place orders, manage
wallets, or provide financial advice.

## Data Sources

The initial external data source is CoinGecko.

The system should collect data such as:

- coin identifier, for example `bitcoin`
- symbol, for example `btc`
- display name, for example `Bitcoin`
- current price in USD
- market capitalization in USD
- 24-hour trading volume in USD
- 24-hour price change percentage
- timestamp when the data was observed
- source name, for example `coingecko`

In the future, the system may support additional sources. The database and
application structure should not assume that CoinGecko is the only possible
provider forever.

## Core Concepts

### Asset

An asset represents a cryptocurrency tracked by the system.

Example assets:

- Bitcoin
- Ethereum
- Solana

The asset table should store relatively stable metadata, such as CoinGecko ID,
symbol, name, and whether the asset is active.

### Price Tick

A price tick is a market data observation for one asset at one point in time.

For example:

```text
bitcoin cost 68000.50 USD at 2026-06-01 10:00:00 UTC
```

Price ticks are append-only historical records. The system should not overwrite
old prices when a new price arrives.

### Ingestion Run

An ingestion run represents one attempt to collect data from an external source.

It should record:

- when the run started
- when the run finished
- whether it succeeded or failed
- how many records were fetched
- how many records were inserted
- an error message if something failed

This is important for data-engineering work because it makes the pipeline
observable and debuggable.

## Database Model

The target database should start with three main tables.

### assets

Stores tracked cryptocurrency metadata.

Suggested columns:

- `id`
- `coin_id`
- `symbol`
- `name`
- `is_active`
- `created_at`
- `updated_at`

Important constraints:

- `coin_id` should be unique
- `symbol` should be indexed if it is used for lookups

### price_ticks

Stores historical market observations.

Suggested columns:

- `id`
- `asset_id`
- `price_usd`
- `market_cap_usd`
- `volume_24h_usd`
- `price_change_24h_percent`
- `observed_at`
- `source`
- `created_at`

Important constraints:

- `asset_id` should reference `assets.id`
- `(asset_id, observed_at, source)` should be unique to avoid duplicate records
- queries by `asset_id` and `observed_at` should be efficient

### ingestion_runs

Stores metadata about data collection jobs.

Suggested columns:

- `id`
- `source`
- `status`
- `started_at`
- `finished_at`
- `records_fetched`
- `records_inserted`
- `error_message`

Possible statuses:

- `running`
- `success`
- `failed`

## Application Layers

The target application should be split into clear layers.

### API Layer

Responsible for HTTP requests and responses.

It should:

- validate path and query parameters
- call services
- return Pydantic response models
- translate known errors into HTTP responses

It should not contain database queries or external API request details.

### Service Layer

Responsible for business logic.

Examples:

- get the latest price for an asset
- collect prices for all active assets
- calculate moving averages
- create an ingestion run and update its final status

### Repository Layer

Responsible for database access.

Examples:

- insert price ticks
- fetch latest price for an asset
- fetch historical prices for a time range
- create or update ingestion run records

The rest of the application should not need to know raw SQLAlchemy query
details.

### Client Layer

Responsible for external API communication.

For CoinGecko, this layer should:

- build request URLs and parameters
- set timeouts
- handle HTTP errors
- parse provider responses into internal data structures

This keeps external API-specific logic out of the rest of the application.

## Target API Endpoints

### Health

```text
GET /health
```

Returns whether the application is running.

```text
GET /ready
```

Returns whether the application can connect to required dependencies such as
PostgreSQL.

### Assets

```text
GET /assets
```

Returns the list of tracked assets.

```text
POST /assets
```

Adds a new asset to track.

```text
PATCH /assets/{coin_id}
```

Updates asset metadata or active status.

### Prices

```text
GET /prices/{coin_id}/latest
```

Returns the latest known price for one asset.

```text
GET /prices/{coin_id}/history
```

Returns historical prices for one asset.

Useful query parameters:

- `from`
- `to`
- `limit`
- `offset`

### Ingestion

```text
POST /ingestion/run
```

Manually starts one ingestion run.

This is useful during development and debugging. In production-like mode,
ingestion should also be scheduled automatically.

```text
GET /ingestion/runs
```

Returns recent ingestion run history.

### Analytics

```text
GET /analytics/{coin_id}/moving-average
```

Returns a simple moving average for an asset.

Useful query parameters:

- `window`
- `from`
- `to`

```text
GET /analytics/top-movers
```

Returns assets with the largest price changes over a selected period.

## Ingestion Flow

A typical ingestion run should work like this:

1. Create an `ingestion_runs` record with status `running`.
2. Load all active assets from the database.
3. Request market data from CoinGecko for those assets.
4. Normalize the external response into internal price tick records.
5. Insert new price ticks into PostgreSQL.
6. Mark the ingestion run as `success`.
7. If an error happens, mark the ingestion run as `failed` and store the error.

The ingestion process should be idempotent where possible. Running the same
ingestion twice should not create duplicate price ticks for the same asset,
timestamp, and source.

## Error Handling

The application should handle expected failures explicitly.

Examples:

- external API timeout
- external API rate limit
- invalid coin ID
- database connection failure
- duplicate asset creation
- no historical data found

API responses should be clear, but internal exception details should not be
leaked to users.

## Observability

The project should include basic observability features:

- structured logs for API requests and ingestion runs
- ingestion run records in the database
- health and readiness endpoints
- clear error messages for failed external API calls

This is important because data pipelines need to be monitored and debugged.

## Testing Strategy

The project should include several levels of tests.

### Unit Tests

Examples:

- cache expiration behavior
- CoinGecko response parsing
- analytics calculations
- service-level error handling

### API Tests

Examples:

- latest price endpoint returns expected shape
- history endpoint supports pagination
- unknown asset returns 404
- invalid query parameters return 422

### Database Tests

Examples:

- price ticks are inserted correctly
- duplicate ticks are rejected or ignored safely
- ingestion runs are updated from `running` to `success` or `failed`

## Local Development

The target local development setup should support:

```text
docker compose up
```

This should start:

- the FastAPI application
- PostgreSQL

Useful developer commands should eventually be added through a Makefile:

```text
make run
make test
make lint
make migrate
make revision
```

## Future Improvements

Possible future additions:

- Redis cache instead of in-memory cache
- Celery, Arq, or APScheduler for background ingestion
- Prometheus metrics
- CSV export
- Parquet export
- partitioned price history tables
- dashboard UI
- support for multiple data providers

These should be added only after the core backend and ingestion flow are solid.
