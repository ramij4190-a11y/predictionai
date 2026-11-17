"""
Corporate Action & Split Normalization Engine.
Computes dual-series price adjustments to eliminate artificial cliff drops from stock splits and bonuses.
"""

from typing import List, Dict, Any
import pandas as pd
import numpy as np


class CorporateActionAdjuster:
    """Computes backward cumulative adjustment factors for splits and bonus issues."""

    @staticmethod
    def adjust_series(
        df_bars: pd.DataFrame, 
        actions: List[Dict[str, Any]]
    ) -> pd.DataFrame:
        """
        Takes raw daily OHLCV and list of corporate actions, and calculates:
        1. close_adj
        2. open_adj, high_adj, low_adj
        
        df_bars must contain: ['trade_date', 'open_unadj', 'high_unadj', 'low_unadj', 'close_unadj', 'volume']
        actions: list of dicts with keys: ['ex_date', 'action_type', 'ratio_from', 'ratio_to', 'adjustment_factor']
        """
        df = df_bars.copy()
        df["trade_date"] = pd.to_datetime(df["trade_date"])
        df = df.sort_values("trade_date").reset_index(drop=True)

        # Initialize cumulative adjustment factor to 1.0 for all rows
        df["cum_factor"] = 1.0

        if actions:
            actions_sorted = sorted(actions, key=lambda x: pd.to_datetime(x["ex_date"]))
            
            for act in actions_sorted:
                ex_date = pd.to_datetime(act["ex_date"])
                factor = float(act["adjustment_factor"])
                
                # Multiply all bars strictly prior to the ex-date by the adjustment factor
                mask = df["trade_date"] < ex_date
                df.loc[mask, "cum_factor"] *= factor

        # Compute adjusted prices
        df["close_adj"] = (df["close_unadj"] * df["cum_factor"]).round(2)
        
        # Invert factor for volume so dollar turnover is preserved
        # (When price is halved, volume is doubled)
        df["volume_adj"] = (df["volume"] / df["cum_factor"]).astype(np.int64)

        return df

