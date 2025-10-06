# EVE Intel - Quickstart Guide

## 🚀 Launch in 3 Commands

```bash
# 1. Clone and configure
cd eve-intel
cp .env.example .env

# 2. Start services (Docker required)
docker-compose up -d

# 3. Seed database
docker-compose exec api python scripts/seed.py
```

## ✅ Verify Installation

```bash
# Health check
curl http://localhost:8000/health

# Get arbitrage signals
curl http://localhost:8000/signals/arbitrage | jq

# Open Grafana dashboard
open http://localhost:3000  # Login: admin/admin
```

## 📊 CLI Usage

```bash
# Find arbitrage opportunities
docker-compose exec api python -m eve_intel.cli find-arb

# With custom filters
docker-compose exec api python -m eve_intel.cli find-arb \
  --min-ev 500000000 \
  --min-margin 10.0 \
  --limit 20 \
  --save-db
```

## 🛠️ Development Mode

```bash
# Install dependencies (requires Poetry)
poetry install

# Run locally
poetry run uvicorn eve_intel.api.main:app --reload

# Run tests
poetry run pytest -v

# Format and lint
poetry run black eve_intel tests
poetry run ruff check eve_intel tests
```

## 🐳 Docker Services

| Service | Port | Purpose |
|---------|------|---------|
| API | 8000 | FastAPI endpoints |
| Grafana | 3000 | Dashboards & viz |
| Postgres | 5432 | OLTP database |
| Redis | 6379 | Cache layer |
| ClickHouse | 8123 | OLAP analytics |

## 📁 Key Files

- `eve_intel/analytics/arbitrage.py` - Core arbitrage engine
- `eve_intel/api/routers/arbitrage.py` - API endpoints
- `eve_intel/cli.py` - CLI commands
- `alembic/versions/` - Database migrations
- `grafana/dashboards/` - Grafana dashboards

## 🔍 API Endpoints

**GET** `/signals/arbitrage`
- Query params: `min_ev`, `min_margin`, `limit`
- Returns: Ranked arbitrage opportunities

**POST** `/signals/arbitrage/analyze`
- Runs fresh analysis
- Query params: `save_results=true`

**GET** `/health`
- System health check

## 📝 Common Tasks

### Run Migrations

```bash
docker-compose exec api alembic upgrade head
```

### View Logs

```bash
docker-compose logs -f api
docker-compose logs -f worker
```

### Database Access

```bash
# PostgreSQL
docker-compose exec postgres psql -U eve_intel_user -d eve_intel

# Redis
docker-compose exec redis redis-cli
```

### Stop Services

```bash
docker-compose down
```

## 🧪 Testing

```bash
# All tests
poetry run pytest

# With coverage
poetry run pytest --cov=eve_intel --cov-report=html

# Specific test
poetry run pytest tests/unit/test_fees.py -v
```

## 🎯 Phase 1 Deliverables

- ✅ Project scaffolded with Poetry
- ✅ Database models + Alembic migrations
- ✅ ESI client with retry/backoff/caching
- ✅ Arbitrage analytics engine
- ✅ FastAPI endpoints (read-only)
- ✅ Typer CLI commands
- ✅ Docker compose stack
- ✅ APScheduler worker
- ✅ Unit tests (70%+ coverage)
- ✅ Grafana dashboard
- ✅ Complete documentation

## 🚦 Next Steps (Phase 2)

1. Integrate real ESI market data
2. Implement ClickHouse analytics
3. Add route risk scoring (zKillboard)
4. Build alert system (Discord/Slack)
5. ML price forecasting
6. Write endpoints (ESI auth)

## 💡 Tips

- Mock data is used in Phase 1 - real ESI integration pending
- Grafana datasource credentials in `.env`
- Worker runs analytics every 4 hours (configurable)
- Sample output: `artifacts/sample_arbitrage.json`

## 🆘 Troubleshooting

**Database connection errors**
```bash
docker-compose restart postgres
docker-compose exec api alembic upgrade head
```

**Port conflicts**
```bash
# Change ports in .env or docker-compose.yml
API_PORT=8001
```

**Redis errors**
```bash
docker-compose restart redis
```

---

**Need help?** Open an issue or check the full README.md
