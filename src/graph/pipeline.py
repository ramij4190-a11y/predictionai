"""
Phase 3 Graph Ontology & Macro Regime Pipeline Orchestrator.
Coordinates relational graph building, macro synchronization, HMM regime classification, and FastDTW pattern analogies.
"""

import time
from rich.console import Console
from rich.table import Table
from src.data.lakehouse import LakehouseManager
from src.graph.ontology_builder import MarketGraphOntology
from src.graph.spillover_engine import NetworkSpilloverEngine
from src.macro.rbi_sync import MacroDataSynchronizer
from src.macro.regime_classifier import MacroRegimeClassifier
from src.analytics.pattern_analogy import HistoricalAnalogyMatcher

console = Console()


class GraphMacroPipeline:
    """Orchestrates Phase 3 graph modeling, macro discovery, and pattern analogies."""

    def __init__(self):
        self.lakehouse = LakehouseManager()
        self.ontology = MarketGraphOntology()
        self.spillover = NetworkSpilloverEngine(self.ontology.graph)
        self.macro_sync = MacroDataSynchronizer(self.lakehouse)
        self.regime_clf = MacroRegimeClassifier()
        self.analogy_matcher = HistoricalAnalogyMatcher(window_size=60, forward_horizon=126)

    def execute_graph_analysis(self) -> None:
        """Runs graph construction and shock diffusion simulation."""
        g = self.ontology.graph
        console.print(f"[bold cyan]Graph Ontology Initialized:[/] {g.number_of_nodes()} Nodes, {g.number_of_edges()} Edges.")

        # Simulate a +20% Brent Crude Spike and +15% Steel Price Inflation
        shock = {
            "MACRO_BRENT_CRUDE": 0.20,
            "MACRO_DOMESTIC_STEEL": 0.15,
            "MACRO_USDINR": 0.05
        }
        impacts = self.spillover.simulate_macro_shock(shock)
        ranked = self.spillover.rank_vulnerabilities(impacts)

        table = Table(title="Graph Simulation: +20% Crude & +15% Steel Shock Transmission", border_style="cyan")
        table.add_column("Symbol", style="bold white")
        table.add_column("Company", style="dim white")
        table.add_column("EBITDA Impact (%)", justify="right")
        table.add_column("Transmission Status", justify="left")

        for item in ranked[:8]:
            imp = item["impact_pct"]
            imp_str = f"[red]{imp:.2f}%[/]" if imp < 0 else f"[green]+{imp:.2f}%[/]"
            table.add_row(item["symbol"], item["company_name"][:24], imp_str, item["regime_status"])

        console.print(table)

    def execute_macro_and_regimes(self) -> None:
        """Syncs macro indicators and classifies current liquidity regime."""
        console.print("[bold green]Syncing Macro Indicators...[/]")
        inserted = self.macro_sync.sync_all_macro(period="5y")
        console.print(f"  Ingested {inserted:,} daily macro observations into DuckDB.")

        # Fetch daily bars across portfolio for regime training
        cursor = self.lakehouse.connect()
        df_prices = cursor.execute("SELECT symbol, trade_date, close_adj FROM daily_ohlcv WHERE symbol IN ('RELIANCE', 'TATAMOTORS', 'INFY', 'TCS', 'HDFCBANK');").df()
        df_macro = cursor.execute("SELECT indicator_id, trade_date, value FROM macro_indicators;").df()

        feat_df = self.regime_clf.prepare_regime_features(df_prices, df_macro)
        if not feat_df.empty:
            self.regime_clf.fit(feat_df)
            current = self.regime_clf.get_current_regime(feat_df)

            console.print("\n[bold yellow]Active Market Regime Discovery (Gaussian HMM):[/]")
            console.print(f"  • Regime State: [bold white]{current['regime_label']}[/]")
            console.print(f"  • Confidence:   [bold cyan]{current['confidence'] * 100:.1f}%[/]")
            for k, v in current["state_probabilities"].items():
                console.print(f"    - {k:35}: {v*100:.1f}%")

    def execute_pattern_analogies(self, symbol: str = "RELIANCE") -> None:
        """Finds top historical analog episodes for a symbol."""
        df_bars = self.lakehouse.get_daily_series(symbol)
        analogs = self.analogy_matcher.find_top_analogs(symbol, df_bars, top_k=3)

        if not analogs:
            console.print(f"[yellow]Insufficient historical data for {symbol} analogy matching.[/]")
            return

        table = Table(title=f"FastDTW Pattern Analogy Cards: {symbol}", border_style="cyan")
        table.add_column("Matched Historical Date", style="bold yellow")
        table.add_column("Similarity Score", justify="right")
        table.add_column("Subsequent 6M Return", justify="right")
        table.add_column("Subsequent Max Rally", justify="right")
        table.add_column("Max Drawdown (6M)", justify="right")

        for a in analogs:
            ret = a["subsequent_6m_return_pct"]
            ret_str = f"[green]+{ret:.2f}%[/]" if ret > 0 else f"[red]{ret:.2f}%[/]"
            table.add_row(
                str(a["match_date"]),
                f"{a['similarity_score'] * 100:.1f}%",
                ret_str,
                f"[green]+{a['subsequent_6m_max_rally_pct']:.2f}%[/]",
                f"[red]{a['subsequent_6m_max_drawdown_pct']:.2f}%[/]"
            )

        console.print(table)


if __name__ == "__main__":
    pipeline = GraphMacroPipeline()
    pipeline.execute_graph_analysis()
    pipeline.execute_macro_and_regimes()
    pipeline.execute_pattern_analogies("RELIANCE")

