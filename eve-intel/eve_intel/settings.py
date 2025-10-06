"""Application settings."""

from typing import List

from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    env: str = Field(default="development")
    log_level: str = Field(default="INFO")
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)

    # Postgres
    postgres_host: str = Field(default="localhost")
    postgres_port: int = Field(default=5432)
    postgres_db: str = Field(default="eve_intel")
    postgres_user: str = Field(default="eve_intel_user")
    postgres_password: str = Field(default="changeme")
    database_url: str = Field(
        default="postgresql+asyncpg://eve_intel_user:changeme@localhost:5432/eve_intel"
    )
    database_url_sync: str = Field(
        default="postgresql+psycopg2://eve_intel_user:changeme@localhost:5432/eve_intel"
    )

    # ClickHouse
    clickhouse_host: str = Field(default="localhost")
    clickhouse_port: int = Field(default=8123)
    clickhouse_db: str = Field(default="eve_intel")
    clickhouse_user: str = Field(default="default")
    clickhouse_password: str = Field(default="")

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0")
    cache_ttl_seconds: int = Field(default=300)

    # ESI API
    esi_base_url: str = Field(default="https://esi.evetech.net/latest")
    esi_user_agent: str = Field(default="eve-intel/0.1.0")
    esi_rate_limit_per_second: int = Field(default=20)
    esi_max_retries: int = Field(default=3)
    esi_backoff_factor: int = Field(default=2)

    # Market hubs
    market_hubs: str = Field(default="60003760,60008494,60011866,60004588,60005686")

    @property
    def market_hub_ids(self) -> List[int]:
        """Parse market hubs into list of integers."""
        return [int(h.strip()) for h in self.market_hubs.split(",") if h.strip()]

    # Trading parameters
    broker_fee_pct: float = Field(default=3.0)
    sales_tax_pct: float = Field(default=8.0)
    min_liquidity_isk_24h: float = Field(default=500_000_000)
    min_ev_isk: float = Field(default=200_000_000)
    min_net_margin_pct: float = Field(default=5.0)
    slippage_buffer_pct: float = Field(default=2.0)

    # Scheduler
    ingestion_cron_schedule: str = Field(default="0 */4 * * *")
    analytics_cron_schedule: str = Field(default="15 */4 * * *")

    # Grafana
    gf_security_admin_user: str = Field(default="admin")
    gf_security_admin_password: str = Field(default="admin")


# Global settings instance
settings = Settings()
