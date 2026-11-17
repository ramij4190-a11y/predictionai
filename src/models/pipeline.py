"""
Phase 4 Directional Forecasting & Invalidation Pipeline Orchestrator.
Trains LightGBM models, projects conformal quantile corridors, and computes structural invalidation floors.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import time
import pandas as pd
import joblib
from rich.console import Console
from rich.table import Table
from src.data.lakehouse import LakehouseManager
from src.data.universe import UniverseManager
from src.models.feature_pipeline import FinancialFeaturePipeline
from src.models.directional_classifier import DirectionalClassifier
from src.models.quantile_corridors import QuantileCorridorRegressor
from src.models.invalidation_engine import InvalidationEngine

console = Console()


class ModelForecastingPipeline:
    """Orchestrates model training, quantile corridor projection, and invalidation analysis."""

    def __init__(self):
        self.lakehouse = LakehouseManager()
        self.universe_mgr = UniverseManager()
        self.feat_pipeline = FinancialFeaturePipeline(self.lakehouse)
        self.classifier = DirectionalClassifier()
        self.quantile_reg = QuantileCorridorRegressor()
        self.models_dir = Path(__file__).resolve().parent.parent.parent / "data" / "models"
        self.models_dir.mkdir(parents=True, exist_ok=True)

    def train_portfolio_models(self, symbols: Optional[List[str]] = None) -> None:
        """
        Gathers features across anchor equities and trains the core forecasting models.
        """
        if symbols is None:
            symbols = ["RELIANCE", "TATAMOTORS", "INFY", "TCS", "HDFCBANK", "ICICIBANK", "LT", "MARUTI"]

        console.print(f"[bold cyan]Assembling Feature Dataset:[/] Extracting features across {len(symbols)} training equities...")
        dfs = []
        for s in symbols:
            df_feat = self.feat_pipeline.extract_features_for_symbol(s)
            if not df_feat.empty:
                dfs.append(df_feat)

        if not dfs:
            raise RuntimeError("No feature records could be extracted from DuckDB.")

        dataset = pd.concat(dfs, ignore_index=True)
        console.print(f"  Extracted {len(dataset):,} valid feature rows across training equities.")

        # 1. Train Directional Classifier with Purged Walk-Forward Splits
        console.print("\n[bold green]Training Directional Classifier (LightGBM)...[/]")
        clf_metrics = self.classifier.train_and_validate(dataset)
        console.print(f"  Purged Walk-Forward Cross-Validation Accuracy: [bold white]{clf_metrics['mean_walk_forward_accuracy_pct']}%\n")

        # 2. Train Quantile Corridor Regressors (5%, 50%, 95%)
        console.print("[bold green]Training Conformal Quantile Corridors (Pinball Loss q05, q50, q95)...[/]")
        self.quantile_reg.fit(dataset, target_col="fwd_ret_60d")
        console.print("  Quantile models successfully fitted.")

        # Serialize trained models to disk
        joblib.dump(self.classifier, self.models_dir / "directional_clf.joblib")
        joblib.dump(self.quantile_reg, self.models_dir / "quantile_corridors.joblib")
        console.print(f"  Saved trained model binaries to [bold yellow]{self.models_dir}[/]\n")

    def generate_portfolio_forecast_matrix(self, symbols: Optional[List[str]] = None) -> None:
        """
        Generates live directional forecast, quantile corridor, and structural invalidation levels.
        """
        if symbols is None:
            symbols = ["RELIANCE", "TATAMOTORS", "INFY", "TCS", "HDFCBANK", "MARUTI", "ASIANPAINT", "HAL"]

        table = Table(title="Project Titan - Directional Forecast & Structural Invalidation Matrix", border_style="cyan")
        table.add_column("Symbol", style="bold white")
        table.add_column("Price (₹)", justify="right")
        table.add_column("Directional Tilt", justify="center")
        table.add_column("Confidence", justify="right")
        table.add_column("60D Median Target", justify="right")
        table.add_column("Corridor Band (5% to 95%)", justify="center")
        table.add_column("Invalidation Floor", style="bold red", justify="right")
        table.add_column("Thesis Status", justify="left")

        for sym in symbols:
            df_feat = self.feat_pipeline.extract_features_for_symbol(sym)
            if df_feat.empty:
                continue

            latest_row = df_feat.iloc[-1:]
            curr_price = float(latest_row["close_unadj"].values[0])

            # 1. Directional Prediction
            dir_res = self.classifier.predict_current_direction(latest_row)
            tilt = dir_res["directional_tilt"]

            if tilt == "BULLISH":
                tilt_badge = "[bold green]BULLISH ▲[/]"
            elif tilt == "BEARISH":
                tilt_badge = "[bold red]BEARISH ▼[/]"
            else:
                tilt_badge = "[yellow]NEUTRAL ▬[/]"

            # 2. Quantile Corridor
            corridor = self.quantile_reg.project_corridor(latest_row, curr_price, horizon_days=60)
            target_str = f"₹{corridor['projected_median_price']:,.2f} ({corridor['projected_median_return_pct']:+.1f}%)"
            band_str = f"₹{corridor['bearish_floor_price_q05']:,.0f} - ₹{corridor['bullish_ceiling_price_q95']:,.0f}"

            # 3. Structural Invalidation
            df_bars = self.lakehouse.get_daily_series(sym)
            inval = InvalidationEngine.calculate_invalidation_floor(df_bars, curr_price, direction=tilt)
            floor_str = f"₹{inval['invalidation_price']:,.2f}"

            status = inval["status"]
            if "WARNING" in status:
                status_str = "[bold red]HIGH ALERT[/]"
            elif "INVALIDATED" in status:
                status_str = "[red]INVALIDATED[/]"
            else:
                status_str = "[green]SOUND[/]"

            table.add_row(
                sym,
                f"₹{curr_price:,.2f}",
                tilt_badge,
                f"{dir_res['confidence_score_pct']:.0f}%",
                target_str,
                band_str,
                floor_str,
                status_str
            )

        console.print(table)


if __name__ == "__main__":
    pipeline = ModelForecastingPipeline()
    pipeline.train_portfolio_models()
    pipeline.generate_portfolio_forecast_matrix()
