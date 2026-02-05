# CLAUDE.md - AI Assistant Guide for EVE Market Intelligence

This document provides essential information for AI assistants working with this codebase.

## Project Overview

**EVE Market Intelligence (eve-intel)** is a production-ready Python system for discovering cross-hub arbitrage opportunities in EVE Online markets. It provides real-time arbitrage signals with full P&L accounting including fees, taxes, and slippage.

**Current Status:** Phase 1 Complete (Mock Data) - Ready for Phase 2 real ESI integration

## Tech Stack

- **Language:** Python 3.13+ (async/await throughout)
- **Web Framework:** FastAPI 0.115+ with Uvicorn
- **Database:** PostgreSQL 16 (asyncpg), ClickHouse (OLAP - Phase 2), Redis 7 (caching)
- **ORM:** SQLAlchemy 2.0+ async with Alembic migrations
- **CLI:** Typer with Rich formatting
- **Scheduler:** APScheduler for background jobs
- **HTTP Client:** httpx with Tenacity retry logic
- **Logging:** Structlog (structured JSON)
- **Package Manager:** Poetry 1.8.3+
- **Containers:** Docker & Docker Compose

## Codebase Structure

```
eve-intel/
├── eve_intel/                    # Main source code
│   ├── analytics/                # Core business logic
│   │   ├── arbitrage.py         # ArbitrageEngine - opportunity discovery
│   │   ├── fees.py              # Fee calculations (broker, sales tax)
│   │   └── risk.py              # Risk scoring, volatility, decay
│   ├── api/                      # FastAPI application
│   │   ├── main.py              # App setup, CORS, lifespan
│   │   └── routers/arbitrage.py # GET/POST signal endpoints
│   ├── datasources/              # External data sources
│   │   ├── esi.py               # EVE Swagger Interface client
│   │   ├── cache.py             # Cache adapter pattern
│   │   └── adapters/mock.py     # Mock ESI for testing
│   ├── db/                       # Database layer
│   │   ├── models.py            # 6 SQLAlchemy ORM models
│   │   ├── base.py              # Session management
│   │   └── repositories.py      # Repository pattern
│   ├── settings.py              # Pydantic config management
│   ├── logging.py               # Structlog configuration
│   ├── cli.py                   # Typer CLI commands
│   └── worker.py                # APScheduler background worker
├── alembic/                      # Database migrations
├── tests/                        # Test suite (pytest)
│   ├── unit/                    # Unit tests
│   └── conftest.py              # Fixtures (async SQLite in-memory)
├── scripts/seed.py              # Database seeding
├── grafana/                      # Monitoring dashboards
├── artifacts/                    # Output samples
└── .github/workflows/ci.yml     # CI/CD pipeline
```

## Development Commands

### Quick Reference (Makefile)

```bash
make install      # Install dependencies with Poetry
make dev          # Install with dev dependencies
make up           # Start all Docker services
make down         # Stop Docker services
make logs         # Tail service logs
make test         # Run pytest with coverage
make fmt          # Format code (Black + Ruff)
make lint         # Run linters (Ruff + Mypy)
make migrate      # Run Alembic migrations
make seed         # Seed database with test data
make find-arb     # Run arbitrage CLI command
make shell        # Open Python shell in container
make psql         # Connect to PostgreSQL
make redis-cli    # Connect to Redis
```

### Running Tests

```bash
# Run all tests with coverage
poetry run pytest --cov=eve_intel --cov-report=term-missing

# Run specific test file
poetry run pytest tests/unit/test_arbitrage.py -v

# Run with coverage HTML report
poetry run pytest --cov=eve_intel --cov-report=html
```

### Starting Development Environment

```bash
# Full stack with Docker
make up           # Starts postgres, redis, clickhouse, api, worker, grafana
make logs         # View logs

# Local development (API only)
poetry run uvicorn eve_intel.api.main:app --reload --port 8000

# Run CLI commands
poetry run python -m eve_intel.cli find-arb --min-ev 100000000 --limit 10
```

## Code Conventions

### Style & Formatting

- **Line length:** 100 characters (Black + Ruff)
- **Formatter:** Black 24.10+
- **Linter:** Ruff 0.7+ (replaces flake8, isort)
- **Type checking:** Mypy strict mode (`disallow_untyped_defs = true`)
- **Pre-commit hooks:** Required before committing

```bash
# Format code
poetry run black .
poetry run ruff check --fix .

# Type check
poetry run mypy eve_intel/
```

### Async Patterns

All database and HTTP operations are async:

```python
# Correct - async database operations
async def get_items(session: AsyncSession) -> list[Item]:
    result = await session.execute(select(Item))
    return result.scalars().all()

# Correct - async HTTP with retry
async with httpx.AsyncClient() as client:
    response = await client.get(url)
```

### Repository Pattern

Use repositories for data access, not direct session queries:

```python
# Correct
items = await ItemRepository(session).get_all()

# Avoid direct queries in business logic
result = await session.execute(select(Item))  # Only in repositories
```

### Configuration

All config via Pydantic Settings with environment variables:

```python
from eve_intel.settings import get_settings

settings = get_settings()
db_url = settings.database_url
```

### Logging

Use structlog throughout:

```python
import structlog
logger = structlog.get_logger()

logger.info("processing_item", item_id=item_id, hub="jita")
```

## Database Schema

6 main tables (see `eve_intel/db/models.py`):

| Table | Purpose |
|-------|---------|
| `items` | EVE item types (id, name, volume) |
| `markets` | Trade hub definitions |
| `orders_snapshot` | Market order snapshots |
| `prices_history` | Daily OHLCV price data |
| `analytics_arbitrage_run` | Analytics run metadata |
| `analytics_arbitrage_item` | Discovered opportunities |

### Migrations

```bash
# Create new migration
poetry run alembic revision --autogenerate -m "description"

# Apply migrations
poetry run alembic upgrade head

# Rollback one version
poetry run alembic downgrade -1
```

## API Endpoints

Base URL: `http://localhost:8000`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/signals/arbitrage` | Get ranked opportunities |
| POST | `/signals/arbitrage/analyze` | Run fresh analysis |
| GET | `/health` | Health check |
| GET | `/docs` | OpenAPI/Swagger UI |

Query parameters for `/signals/arbitrage`:
- `min_ev` - Minimum expected value ISK (default: 200M)
- `min_margin` - Minimum net margin % (default: 5.0)
- `limit` - Max results 1-1000 (default: 50)

## Testing Conventions

- **Framework:** pytest with pytest-asyncio
- **Coverage minimum:** 35% (enforced in CI)
- **Test database:** SQLite in-memory (async via aiosqlite)
- **Fixtures:** See `tests/conftest.py`

```python
# Test naming convention
def test_calculate_broker_fee_standard_rate():
    ...

# Async test example
@pytest.mark.asyncio
async def test_repository_get_item(db_session):
    repo = ItemRepository(db_session)
    ...
```

## Environment Variables

Key variables (see `.env.example` for complete list):

```bash
# Required
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/eve_intel
REDIS_URL=redis://localhost:6379/0

# Market settings
BROKER_FEE_PCT=3.0
SALES_TAX_PCT=8.0
MIN_EV_ISK=200000000
MIN_NET_MARGIN_PCT=5.0

# ESI API
ESI_BASE_URL=https://esi.evetech.net/latest
ESI_RATE_LIMIT_PER_SECOND=20
```

## Docker Services

| Service | Port | Health Check |
|---------|------|--------------|
| postgres | 5432 | pg_isready |
| redis | 6379 | redis-cli ping |
| clickhouse | 8123, 9000 | wget /ping |
| api | 8000 | /health |
| grafana | 3000 | - |

## Common Tasks for AI Assistants

### Adding a New API Endpoint

1. Add route in `eve_intel/api/routers/` or create new router
2. Register router in `eve_intel/api/main.py`
3. Add Pydantic schemas for request/response
4. Add tests in `tests/unit/`

### Adding a New Database Table

1. Add model in `eve_intel/db/models.py`
2. Create migration: `poetry run alembic revision --autogenerate -m "add_table"`
3. Add repository in `eve_intel/db/repositories.py`
4. Add tests for repository

### Adding Analytics Feature

1. Implement in `eve_intel/analytics/`
2. Follow existing patterns (ArbitrageEngine)
3. Use async operations
4. Add comprehensive tests

### Modifying Fee/Risk Calculations

1. Update `eve_intel/analytics/fees.py` or `risk.py`
2. Ensure backward compatibility
3. Add/update tests - these are critical business logic

## Important Patterns

### Dependency Injection (FastAPI)

```python
from eve_intel.db.base import get_db

@router.get("/items")
async def get_items(session: AsyncSession = Depends(get_db)):
    ...
```

### Error Handling

Use structured exceptions with logging:

```python
try:
    result = await operation()
except SomeError as e:
    logger.error("operation_failed", error=str(e), context=ctx)
    raise HTTPException(status_code=500, detail="Operation failed")
```

### Cache Pattern

```python
from eve_intel.datasources.cache import CacheAdapter

cache = CacheAdapter(redis_client, ttl_seconds=300)
cached_data = await cache.get_or_set(key, fetch_func)
```

## Phase 2 Roadmap (Not Yet Implemented)

- Real ESI market data integration
- ClickHouse analytics queries
- zKillboard route risk scoring
- Discord/Slack alert webhooks
- Portfolio tracking
- ML price forecasting

## Troubleshooting

### Database connection issues
```bash
make psql  # Test direct connection
docker compose logs postgres  # Check postgres logs
```

### Test failures
```bash
poetry run pytest -v --tb=short  # Verbose with short traceback
poetry run pytest --lf  # Run only last failed tests
```

### Type checking errors
```bash
poetry run mypy eve_intel/ --show-error-codes
```

## CI/CD Pipeline

GitHub Actions runs on push/PR to main/develop:
1. Ruff linting
2. Black formatting check
3. Mypy type checking
4. pytest with coverage (35% minimum)
5. Coverage upload to Codecov

All checks must pass before merge.

## Files to Never Modify Without Care

- `alembic/versions/` - Database migrations (append-only)
- `pyproject.toml` - Dependency versions
- `.github/workflows/ci.yml` - CI pipeline
- `eve_intel/db/models.py` - Schema changes need migrations
