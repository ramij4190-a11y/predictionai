"""
Master Ingestion Pipeline Orchestrator.
Coordinates universe loading, historical backfill, and DuckDB lakehouse population.
"""

from typing import List, Optional
import time
from rich.console import Console
from rich.table import Table
from src.data.universe import UniverseManager
from src.data.lakehouse import LakehouseManager
from src.data.bhavcopy_fetcher import MarketDataFetcher

console = Console()


class IngestionPipeline:
    """Coordinates universe seeding and time-series backfilling into DuckDB."""

    def __init__(self):
        self.universe_mgr = UniverseManager()
        self.lakehouse = LakehouseManager()
        self.fetcher = MarketDataFetcher()

    def initialize_lakehouse(self) -> None:
        """Seeds the 50-stock registry into the DuckDB catalog."""
        equities = self.universe_mgr.get_all()
        count = self.lakehouse.seed_universe(equities)
        console.print(f"[bold cyan]Initialized Lakehouse:[/] Seeded {count} equities into metadata registry.")

    def backfill_symbols(
        self, 
        symbols: Optional[List[str]] = None, 
        period: str = "2y"
    ) -> int:
        """
        Backfills historical data for specified symbols (or all 50 if None).
        Inserts cleaned, dual-series records into DuckDB.
        """
        if symbols is None:
            symbols = self.universe_mgr.get_symbols()

        total_bars_inserted = 0
        start_time = time.time()

        console.print(f"[bold green]Starting Backfill:[/] Ingesting {len(symbols)} symbols (Period: {period})...")

        for idx, sym in enumerate(symbols, 1):
            try:
                df_bars = self.fetcher.fetch_historical(sym, period=period)
                if not df_bars.empty:
                    inserted = self.lakehouse.insert_daily_bars(df_bars)
                    total_bars_inserted += inserted
                    console.print(f"  [{idx}/{len(symbols)}] [green]OK[/] {sym:12} : Ingested {inserted} daily bars.")
                else:
                    console.print(f"  [{idx}/{len(symbols)}] [yellow]WARN[/] {sym:12} : No data returned.")
            except Exception as e:
                console.print(f"  [{idx}/{len(symbols)}] [red]FAIL[/] {sym:12} : {e}")

        elapsed = time.time() - start_time
        console.print(f"\n[bold green]Ingestion Complete:[/] Inserted {total_bars_inserted:,} total bars in {elapsed:.2f} seconds.")
        return total_bars_inserted

    def print_market_summary(self) -> None:
        """Displays summary telemetry matrix across the ingested equities."""
        df_summary = self.lakehouse.get_market_summary()
        
        if df_summary.empty:
            console.print("[yellow]No market data currently ingested in DuckDB.[/]")
            return

        table = Table(title="Project Titan - 50 Indian Equities Market Summary", border_style="cyan")
        table.add_column("Symbol", style="bold white", justify="left")
        table.add_column("Company", style="dim white", justify="left")
        table.add_column("Sector", style="cyan", justify="left")
        table.add_column("Price (₹)", style="bold yellow", justify="right")
        table.add_column("Adj Price (₹)", style="yellow", justify="right")
        table.add_column("20D Return (%)", justify="right")
        table.add_column("Delivery (%)", justify="right")

        for _, row in df_summary.iterrows():
            ret = row["return_20d_pct"]
            if ret > 0:
                ret_str = f"[green]+{ret:.2f}%[/]"
            elif ret < 0:
                ret_str = f"[red]{ret:.2f}%[/]"
            else:
                ret_str = f"{ret:.2f}%"

            table.add_row(
                str(row["symbol"]),
                str(row["company_name"])[:26],
                str(row["sector"]),
                f"₹{row['current_price']:,.2f}",
                f"₹{row['current_price_adj']:,.2f}",
                ret_str,
                f"{row['latest_delivery_pct']:.1f}%"
            )

        console.print(table)


if __name__ == "__main__":
    import sys
    pipeline = IngestionPipeline()
    pipeline.initialize_lakehouse()
    
    # Check command-line argument for period, default to 5y
    period = sys.argv[1] if len(sys.argv) > 1 else "5y"
    pipeline.backfill_symbols(symbols=None, period=period)
    pipeline.print_market_summary()
