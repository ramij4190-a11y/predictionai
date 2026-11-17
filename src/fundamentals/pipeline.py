"""
Phase 2 Fundamentals & BSE Announcement Pipeline Orchestrator.
Coordinates Point-in-Time financial statement backfills and corporate announcement scoring into DuckDB.
"""

from typing import List, Optional
import time
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from src.data.universe import UniverseManager
from src.data.lakehouse import LakehouseManager
from src.fundamentals.screener_client import FundamentalDataFetcher
from src.fundamentals.bse_announcements import CorporateAnnouncementWatcher
from src.fundamentals.local_nlp import LocalNLPExtractor

console = Console()


class FundamentalPipeline:
    """Orchestrates quarterly fundamentals and announcement ingestion."""

    def __init__(self):
        self.universe_mgr = UniverseManager()
        self.lakehouse = LakehouseManager()
        self.fetcher = FundamentalDataFetcher()
        self.ann_watcher = CorporateAnnouncementWatcher()
        self.nlp = LocalNLPExtractor()

    def backfill_fundamentals(self, symbols: Optional[List[str]] = None) -> int:
        """
        Backfills historical quarterly balance sheets, EBITDA margins, and promoter holdings.
        Enforces Point-in-Time filing timestamps.
        """
        if symbols is None:
            symbols = self.universe_mgr.get_symbols()

        total_inserted = 0
        start_time = time.time()
        console.print(f"[bold green]Starting Fundamentals Backfill:[/] Processing {len(symbols)} equities...")

        for idx, sym in enumerate(symbols, 1):
            try:
                df_fund = self.fetcher.fetch_quarterly_fundamentals(sym)
                if not df_fund.empty:
                    inserted = self.lakehouse.insert_fundamentals(df_fund)
                    total_inserted += inserted
                    latest_mrg = df_fund.iloc[-1]["ebitda_margin_pct"]
                    console.print(f"  [{idx}/{len(symbols)}] [green]OK[/] {sym:12} : {inserted} quarters (Latest EBITDA Margin: {latest_mrg:.1f}%)")
                else:
                    console.print(f"  [{idx}/{len(symbols)}] [yellow]WARN[/] {sym:12} : No quarterly data available.")
            except Exception as e:
                console.print(f"  [{idx}/{len(symbols)}] [red]FAIL[/] {sym:12} : {e}")

        elapsed = time.time() - start_time
        console.print(f"\n[bold green]Fundamentals Ingestion Complete:[/] Inserted {total_inserted} quarterly statements in {elapsed:.2f}s.\n")
        return total_inserted

    def ingest_sample_announcements(self) -> int:
        """
        Populates sample high-materiality corporate announcements (Results, Order Wins, Promoter Pledges)
        for primary equities to test alerting and NLP extraction.
        """
        now = datetime.now()
        sample_announcements = [
            {
                "symbol": "TATAMOTORS",
                "headline": "Tata Motors Passenger Vehicles bags major commercial mobility contract worth Rs 1,450 Crores from state transport utilities.",
                "category": "Order Win",
                "announcement_timestamp": now - timedelta(days=2, hours=4)
            },
            {
                "symbol": "RELIANCE",
                "headline": "Outcome of Board Meeting: Unaudited Financial Results for Q2 with Revenue of Rs 2,35,000 Crores and record retail EBITDA.",
                "category": "Financial Results",
                "announcement_timestamp": now - timedelta(days=5, hours=1)
            },
            {
                "symbol": "BAJFINANCE",
                "headline": "Disclosure under Regulation 31(1) of SAST: Revocation of pledge on 2.4% promoter shares.",
                "category": "Promoter Share Pledging",
                "announcement_timestamp": now - timedelta(days=8, hours=2)
            },
            {
                "symbol": "HAL",
                "headline": "Hindustan Aeronautics receives Letter of Award for supply of advanced avionics worth Rs 2,800 Crores from Ministry of Defence.",
                "category": "Order Win",
                "announcement_timestamp": now - timedelta(days=12, hours=6)
            },
            {
                "symbol": "INFY",
                "headline": "Infosys expands global enterprise AI partnership with major cloud provider; expects margin expansion.",
                "category": "Strategic Collaboration",
                "announcement_timestamp": now - timedelta(days=18, hours=3)
            }
        ]

        # Process through announcement watcher and NLP extractor
        items_to_insert = []
        for ann in sample_announcements:
            nlp_data = self.nlp.extract_entities(ann["headline"])
            ann["extracted_data"] = nlp_data
            items_to_insert.append(ann)

        df_ann = self.ann_watcher.parse_raw_announcements("SYSTEM", items_to_insert)
        count = self.lakehouse.insert_announcements(df_ann)
        console.print(f"[bold cyan]Ingested Announcements:[/] Populated {count} scored corporate announcements.")
        return count

    def print_fundamental_summary(self, symbol: str = "RELIANCE") -> None:
        """Displays Point-in-Time quarterly results for a symbol."""
        df_pit = self.lakehouse.get_pit_fundamentals(symbol)
        if df_pit.empty:
            console.print(f"[yellow]No fundamental records found for {symbol}.[/]")
            return

        table = Table(title=f"Point-in-Time Fundamentals: {symbol}", border_style="cyan")
        table.add_column("Period End", style="bold white")
        table.add_column("Filing Timestamp (PIT)", style="yellow")
        table.add_column("Revenue (₹ Cr)", justify="right")
        table.add_column("EBITDA (₹ Cr)", justify="right")
        table.add_column("EBITDA Margin", justify="right")
        table.add_column("Debt/Equity", justify="right")
        table.add_column("Promoter %", justify="right")
        table.add_column("Pledged %", justify="right")

        for _, row in df_pit.iterrows():
            mrg = row["ebitda_margin_pct"]
            mrg_str = f"[green]{mrg:.1f}%[/]" if mrg > 15 else f"[yellow]{mrg:.1f}%[/]"

            table.add_row(
                str(row["period_end_date"]),
                str(row["filing_timestamp"])[:16],
                f"₹{row['revenue_cr']:,.1f}",
                f"₹{row['ebitda_cr']:,.1f}",
                mrg_str,
                f"{row['debt_to_equity']:.2f}",
                f"{row['promoter_holding_pct']:.1f}%",
                f"{row['pledged_promoter_pct']:.1f}%"
            )

        console.print(table)


if __name__ == "__main__":
    pipeline = FundamentalPipeline()
    # Test on key anchor stocks
    test_symbols = ["TATAMOTORS", "RELIANCE", "INFY", "HDFCBANK", "TCS"]
    pipeline.backfill_fundamentals(test_symbols)
    pipeline.ingest_sample_announcements()
    pipeline.print_fundamental_summary("RELIANCE")

