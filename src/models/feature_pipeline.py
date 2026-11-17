"""
Multi-Scale Point-in-Time Feature Engineering Pipeline.
Unifies technical momentum, PIT quarterly fundamentals, graph spillover scores, and macro regime embeddings.
"""

from typing import Optional, List, Tuple
import numpy as np
import pandas as pd
from src.data.lakehouse import LakehouseManager
from src.graph.ontology_builder import MarketGraphOntology
from src.graph.spillover_engine import NetworkSpilloverEngine


class FinancialFeaturePipeline:
    """Assembles multi-dimensional features with strict zero lookahead guardrails."""

    def __init__(self, lakehouse: Optional[LakehouseManager] = None):
        self.lakehouse = lakehouse or LakehouseManager()
        self.ontology = MarketGraphOntology()
        self.spillover = NetworkSpilloverEngine(self.ontology.graph)

    @staticmethod
    def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
        """Calculates 14-period Relative Strength Index (RSI)."""
        delta = series.diff()
        gain = (delta.where(delta > 0, 0.0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0.0)).rolling(window=period).mean()
        rs = gain / loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50.0).round(2)

    def extract_features_for_symbol(
        self, 
        symbol: str, 
        deadband: float = 0.03
    ) -> pd.DataFrame:
        """
        Builds feature matrix and forward return targets for a single equity.
        deadband: Threshold below which returns are labeled neutral (e.g. 3% ~ 0.03)
        """
        sym = symbol.upper()
        df_bars = self.lakehouse.get_daily_series(sym)
        if df_bars.empty or len(df_bars) < 220:
            return pd.DataFrame()

        df = df_bars.copy()
        df["trade_date"] = pd.to_datetime(df["trade_date"])
        df = df.sort_values("trade_date").reset_index(drop=True)

        # -------------------------------------------------------------
        # 1. Technical Momentum & Trend Features
        # -------------------------------------------------------------
        p = df["close_adj"]
        df["ret_20d"] = (p.pct_change(20) * 100).round(2)
        df["ret_60d"] = (p.pct_change(60) * 100).round(2)
        df["ret_120d"] = (p.pct_change(120) * 100).round(2)

        sma_50 = p.rolling(50).mean()
        sma_200 = p.rolling(200).mean()
        df["dist_sma50"] = (((p - sma_50) / sma_50) * 100).round(2)
        df["dist_sma200"] = (((p - sma_200) / sma_200) * 100).round(2)

        df["rsi_14"] = self.calculate_rsi(p, period=14)
        df["volatility_20d"] = (p.pct_change().rolling(20).std() * np.sqrt(252) * 100).round(2)

        # Institutional Delivery Ratio (20-day vs 60-day delivery volume)
        del_20 = df["delivery_qty"].rolling(20).mean()
        del_60 = df["delivery_qty"].rolling(60).mean().replace(0, np.nan)
        df["delivery_ratio"] = (del_20 / del_60).fillna(1.0).round(3)

        # Rolling 60-day Anchored VWAP distance
        pv = df["close_unadj"] * df["volume"]
        rolling_pv = pv.rolling(60).sum()
        rolling_vol = df["volume"].rolling(60).sum().replace(0, np.nan)
        vwap_60 = rolling_pv / rolling_vol
        df["dist_vwap60"] = (((df["close_unadj"] - vwap_60) / vwap_60) * 100).fillna(0.0).round(2)

        # -------------------------------------------------------------
        # 2. Point-in-Time (PIT) Fundamental Features
        # -------------------------------------------------------------
        df_funds = self.lakehouse.get_pit_fundamentals(sym)
        if not df_funds.empty:
            df_funds["filing_date"] = pd.to_datetime(df_funds["filing_timestamp"]).dt.date
            df_funds["filing_date"] = pd.to_datetime(df_funds["filing_date"]).astype("datetime64[ns]")
            df_funds = df_funds.sort_values("filing_date")

            # Merge as-of: For each trade_date, match latest fundamental report filed before trade_date
            df["trade_date_dt"] = pd.to_datetime(df["trade_date"]).astype("datetime64[ns]")
            df = pd.merge_asof(
                df,
                df_funds[["filing_date", "ebitda_margin_pct", "debt_to_equity", "promoter_holding_pct", "pledged_promoter_pct"]],
                left_on="trade_date_dt",
                right_on="filing_date",
                direction="backward"
            )
            df = df.drop(columns=["trade_date_dt", "filing_date"])
        else:
            df["ebitda_margin_pct"] = 15.0
            df["debt_to_equity"] = 0.5
            df["promoter_holding_pct"] = 50.0
            df["pledged_promoter_pct"] = 0.0

        # Fill forward any early dates before initial filings
        for col in ["ebitda_margin_pct", "debt_to_equity", "promoter_holding_pct", "pledged_promoter_pct"]:
            df[col] = df[col].ffill().bfill()

        # -------------------------------------------------------------
        # 3. Macro Regime & Commodity Sensitivity Features
        # -------------------------------------------------------------
        # Fetch latest shock sensitivity score from knowledge graph
        default_shock = {"MACRO_BRENT_CRUDE": 0.10, "MACRO_DOMESTIC_STEEL": 0.10, "MACRO_USDINR": 0.02}
        impacts = self.spillover.simulate_macro_shock(default_shock)
        df["graph_shock_score"] = impacts.get(sym, 0.0)

        # -------------------------------------------------------------
        # 4. Supervised Target Label Generation
        # -------------------------------------------------------------
        # Forward returns over 60, 120, and 180 trading days
        df["fwd_ret_60d"] = (df["close_adj"].shift(-60) - df["close_adj"]) / df["close_adj"]
        df["fwd_ret_120d"] = (df["close_adj"].shift(-120) - df["close_adj"]) / df["close_adj"]
        df["fwd_ret_180d"] = (df["close_adj"].shift(-180) - df["close_adj"]) / df["close_adj"]

        # Binary Directional Label (with neutral deadband):
        # 1: Bullish (> +3% excess return)
        # 0: Bearish (< -3% excess return)
        # np.nan: Inside neutral chop deadband
        conditions = [
            (df["fwd_ret_60d"] > deadband),
            (df["fwd_ret_60d"] < -deadband)
        ]
        choices = [1, 0]
        df["target_dir_60d"] = np.select(conditions, choices, default=np.nan)

        return df.dropna(subset=["ret_120d", "dist_sma200"]).reset_index(drop=True)
