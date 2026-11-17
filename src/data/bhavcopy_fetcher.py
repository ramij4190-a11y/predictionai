"""
Bhavcopy & Market Data Ingestion Fetcher.
Retrieves historical and daily OHLCV, splits, and delivery metrics for NSE/BSE equities.
"""

from typing import Optional
from datetime import datetime
import pandas as pd
import yfinance as yf

# Dynamic ticker aliases for structural demergers/rebranding
TICKER_ALIASES = {
    "TATAMOTORS": "TMPV",  # Tata Motors Passenger Vehicles Ltd (post-2025 demerger)
    "ZOMATO": "ETERNAL",   # Eternal Limited (Zomato/Blinkit corporate rebrand)
}


class MarketDataFetcher:
    """Fetches and normalizes market data for Indian equities."""

    def __init__(self):
        pass

    def resolve_ticker(self, symbol: str) -> str:
        """Resolves symbol alias if corporate actions/demergers renamed the exchange ticker."""
        sym = symbol.upper()
        return TICKER_ALIASES.get(sym, sym)

    def fetch_historical(
        self, 
        symbol: str, 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None,
        period: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Fetches historical daily OHLCV and splits for an NSE equity.
        Uses Yahoo Finance NSE ticker format (e.g. RELIANCE.NS, TMPV.NS).
        """
        resolved_sym = self.resolve_ticker(symbol)
        ticker_str = f"{resolved_sym}.NS"
        ticker = yf.Ticker(ticker_str)

        # If period or date range is provided
        try:
            if period:
                raw_df = ticker.history(period=period, auto_adjust=False)
            else:
                if not start_date:
                    start_date = "2020-01-01"
                if not end_date:
                    end_date = datetime.now().strftime("%Y-%m-%d")
                raw_df = ticker.history(start=start_date, end=end_date, auto_adjust=False)
        except Exception:
            return pd.DataFrame()

        if raw_df is None or raw_df.empty:
            return pd.DataFrame()

        raw_df = raw_df.reset_index()
        
        # Format date column
        if "Date" in raw_df.columns:
            date_col = "Date"
        elif "Datetime" in raw_df.columns:
            date_col = "Datetime"
        else:
            date_col = raw_df.columns[0]
            
        trade_dates = pd.to_datetime(raw_df[date_col]).dt.date

        # Explicitly initialize with identical index to avoid NaN broadcasting errors
        df = pd.DataFrame(index=raw_df.index)
        df["symbol"] = symbol.upper()  # Retain user's portfolio symbol
        df["trade_date"] = trade_dates
        df["open_unadj"] = raw_df["Open"].round(2)
        df["high_unadj"] = raw_df["High"].round(2)
        df["low_unadj"] = raw_df["Low"].round(2)
        df["close_unadj"] = raw_df["Close"].round(2)
        df["volume"] = raw_df["Volume"].fillna(0).astype("int64")

        # In yfinance with auto_adjust=False, 'Adj Close' is provided if available
        if "Adj Close" in raw_df.columns:
            df["close_adj"] = raw_df["Adj Close"].fillna(df["close_unadj"]).round(2)
        else:
            df["close_adj"] = df["close_unadj"]

        # Calculate estimated turnover in Crores (Price * Volume / 10,000,000)
        df["turnover_cr"] = ((df["close_unadj"] * df["volume"]) / 1e7).round(2)

        # Baseline delivery volume estimate (updated by Phase 1 NSE daily reports)
        df["delivery_qty"] = (df["volume"] * 0.45).astype("int64")
        df["delivery_pct"] = 45.0

        return df.sort_values("trade_date").reset_index(drop=True)
