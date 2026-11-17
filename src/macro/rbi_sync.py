"""
Macroeconomic Synchronizer & Fetcher.
Retrieves Brent Crude, USD/INR, US 10Y Yield, and domestic interest rate indicators.
"""

from typing import List, Dict, Optional
from datetime import datetime, date
import pandas as pd
import yfinance as yf
from src.data.lakehouse import LakehouseManager


class MacroDataSynchronizer:
    """Synchronizes systemic macroeconomic and commodity indicators into DuckDB."""

    INDICATORS = {
        "MACRO_BRENT_CRUDE": "BZ=F",       # Brent Crude Oil ($/barrel)
        "MACRO_USDINR": "USDINR=X",        # USD/INR Currency Pair
        "MACRO_US_10Y": "^TNX",            # US 10-Year Treasury Yield
    }

    def __init__(self, lakehouse: Optional[LakehouseManager] = None):
        self.lakehouse = lakehouse or LakehouseManager()
        self._init_macro_table()

    def _init_macro_table(self) -> None:
        """Initializes macro_indicators table in DuckDB."""
        cursor = self.lakehouse.connect()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS macro_indicators (
                indicator_id VARCHAR NOT NULL,
                trade_date DATE NOT NULL,
                value DOUBLE NOT NULL,
                change_1d_pct DOUBLE DEFAULT 0.0,
                change_20d_pct DOUBLE DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (indicator_id, trade_date)
            );
            CREATE INDEX IF NOT EXISTS idx_macro_id_date ON macro_indicators (indicator_id, trade_date);
        """)

    def fetch_indicator_history(self, indicator_id: str, period: str = "5y") -> pd.DataFrame:
        """Fetches historical time series for a single macro indicator."""
        ticker_str = self.INDICATORS.get(indicator_id)
        if not ticker_str:
            return pd.DataFrame()

        try:
            ticker = yf.Ticker(ticker_str)
            raw_df = ticker.history(period=period, auto_adjust=False)
        except Exception:
            return pd.DataFrame()

        if raw_df is None or raw_df.empty:
            return pd.DataFrame()

        raw_df = raw_df.reset_index()
        date_col = "Date" if "Date" in raw_df.columns else raw_df.columns[0]
        dates = pd.to_datetime(raw_df[date_col]).dt.date

        df = pd.DataFrame(index=raw_df.index)
        df["indicator_id"] = indicator_id
        df["trade_date"] = dates
        df["value"] = raw_df["Close"].round(2)
        df["change_1d_pct"] = (raw_df["Close"].pct_change() * 100).fillna(0.0).round(2)
        df["change_20d_pct"] = (raw_df["Close"].pct_change(periods=20) * 100).fillna(0.0).round(2)

        return df.sort_values("trade_date").reset_index(drop=True)

    def sync_all_macro(self, period: str = "5y") -> int:
        """Fetches and inserts all configured macro indicators into DuckDB."""
        total_inserted = 0
        cursor = self.lakehouse.connect()

        for ind_id in self.INDICATORS.keys():
            df = self.fetch_indicator_history(ind_id, period=period)
            if not df.empty:
                cursor.register("df_macro_temp", df)
                cursor.execute("""
                    INSERT OR REPLACE INTO macro_indicators (indicator_id, trade_date, value, change_1d_pct, change_20d_pct, created_at)
                    SELECT indicator_id, trade_date, value, change_1d_pct, change_20d_pct, CURRENT_TIMESTAMP
                    FROM df_macro_temp;
                """)
                cursor.unregister("df_macro_temp")
                total_inserted += len(df)

        return total_inserted

    def get_latest_macro_snapshot(self) -> Dict[str, float]:
        """Returns the most recent reading for each macro indicator."""
        cursor = self.lakehouse.connect()
        query = """
            WITH ranked AS (
                SELECT indicator_id, value, change_20d_pct,
                       ROW_NUMBER() OVER (PARTITION BY indicator_id ORDER BY trade_date DESC) as rank
                FROM macro_indicators
            )
            SELECT indicator_id, value, change_20d_pct FROM ranked WHERE rank = 1;
        """
        df = cursor.execute(query).df()
        return dict(zip(df["indicator_id"], df["value"]))

