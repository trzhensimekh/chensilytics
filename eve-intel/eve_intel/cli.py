"""CLI commands using Typer."""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from eve_intel.analytics.arbitrage import ArbitrageEngine
from eve_intel.db.base import get_db_session
from eve_intel.logging import configure_logging, get_logger

app = typer.Typer(help="EVE Market Intelligence CLI")
console = Console()
logger = get_logger(__name__)


@app.command()
def find_arb(
    min_ev: float = typer.Option(200_000_000, help="Minimum expected value (ISK)"),
    min_margin: float = typer.Option(5.0, help="Minimum net margin %"),
    limit: int = typer.Option(50, help="Max results to display"),
    output_file: Optional[str] = typer.Option(None, help="Output JSON file path"),
    save_db: bool = typer.Option(False, "--save-db", help="Save results to database"),
) -> None:
    """
    Find arbitrage opportunities.

    Analyzes market data and displays top arbitrage candidates.
    """
    configure_logging()

    async def _run() -> None:
        async with get_db_session() as session:
            engine = ArbitrageEngine(session)

            console.print(f"[bold cyan]Searching for arbitrage opportunities...[/bold cyan]")
            console.print(f"Min EV: {min_ev:,.0f} ISK")
            console.print(f"Min Margin: {min_margin:.1f}%")
            console.print()

            candidates = await engine.find_arbitrage_opportunities(
                min_ev_isk=min_ev,
                min_margin_pct=min_margin,
            )

            candidates = candidates[:limit]

            # Display as table
            table = Table(title="Arbitrage Opportunities", show_lines=True)
            table.add_column("Item ID", style="cyan")
            table.add_column("From Hub", style="green")
            table.add_column("To Hub", style="green")
            table.add_column("Buy Price", style="yellow", justify="right")
            table.add_column("Sell Price", style="yellow", justify="right")
            table.add_column("Margin %", style="magenta", justify="right")
            table.add_column("EV (M ISK)", style="red", justify="right")
            table.add_column("Decay Score", style="blue", justify="right")

            for c in candidates:
                table.add_row(
                    str(c.item_id),
                    str(c.from_hub_id),
                    str(c.to_hub_id),
                    f"{c.buy_price:,.2f}",
                    f"{c.sell_price:,.2f}",
                    f"{c.net_margin_pct:.2f}",
                    f"{c.ev_isk / 1_000_000:.1f}",
                    f"{c.decay_score:.1f}",
                )

            console.print(table)
            console.print(f"\n[bold green]Found {len(candidates)} opportunities[/bold green]")

            # Save to file if requested
            if output_file or not output_file:
                # Default output path
                timestamp = datetime.now().strftime("%Y%m%d_%H%M")
                output_path = Path(output_file or f"artifacts/arbitrage_{timestamp}.json")
                output_path.parent.mkdir(parents=True, exist_ok=True)

                data = {
                    "timestamp": datetime.now().isoformat(),
                    "params": {
                        "min_ev_isk": min_ev,
                        "min_margin_pct": min_margin,
                    },
                    "count": len(candidates),
                    "opportunities": [
                        {
                            "item_id": c.item_id,
                            "from_hub": c.from_hub_id,
                            "to_hub": c.to_hub_id,
                            "buy_price": c.buy_price,
                            "sell_price": c.sell_price,
                            "net_margin_pct": c.net_margin_pct,
                            "ev_isk": c.ev_isk,
                            "daily_liquidity": c.liquidity_24h,
                            "capital_required": c.capital_required,
                            "decay_score": c.decay_score,
                        }
                        for c in candidates
                    ],
                }

                with open(output_path, "w") as f:
                    json.dump(data, f, indent=2)

                console.print(f"\n[bold]Saved to {output_path}[/bold]")

            # Save to DB if requested
            if save_db and candidates:
                run_id = await engine.save_run_results(candidates)
                console.print(f"\n[bold]Saved to database (run_id={run_id})[/bold]")

    asyncio.run(_run())


@app.command()
def db_migrate(
    revision: str = typer.Option("head", help="Alembic revision target"),
) -> None:
    """Run database migrations."""
    import subprocess

    console.print(f"[bold cyan]Running migrations to {revision}...[/bold cyan]")
    result = subprocess.run(["alembic", "upgrade", revision], capture_output=True, text=True)

    if result.returncode == 0:
        console.print("[bold green]Migrations completed successfully[/bold green]")
    else:
        console.print(f"[bold red]Migration failed:[/bold red]\n{result.stderr}")
        raise typer.Exit(1)


@app.command()
def db_downgrade(
    revision: str = typer.Option("-1", help="Alembic revision target"),
) -> None:
    """Downgrade database migrations."""
    import subprocess

    console.print(f"[bold cyan]Downgrading to {revision}...[/bold cyan]")
    result = subprocess.run(["alembic", "downgrade", revision], capture_output=True, text=True)

    if result.returncode == 0:
        console.print("[bold green]Downgrade completed successfully[/bold green]")
    else:
        console.print(f"[bold red]Downgrade failed:[/bold red]\n{result.stderr}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
