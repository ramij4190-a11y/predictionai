"""
Structural Invalidation & Stop-Loss Engine.
Computes mathematical invalidation floors, anchored VWAP boundaries, and proximity alerts.
"""

from typing import Dict, Any, Optional
import numpy as np
import pandas as pd


class InvalidationEngine:
    """Calculates non-negotiable structural invalidation levels for directional theses."""

    @staticmethod
    def calculate_invalidation_floor(
        df_bars: pd.DataFrame, 
        current_price: float, 
        direction: str = "BULLISH",
        lookback_days: int = 60
    ) -> Dict[str, Any]:
        """
        Calculates the structural invalidation price floor/ceiling.
        df_bars must contain: ['low_unadj', 'high_unadj', 'close_unadj', 'volume']
        """
        if len(df_bars) < 20:
            floor = round(current_price * 0.92, 2)
            return {
                "invalidation_price": floor,
                "invalidation_type": "DEFAULT_8PCT",
                "status": "STRUCTURALLY_SOUND",
                "distance_to_invalidation_pct": 8.0
            }

        recent_bars = df_bars.tail(lookback_days)

        if "BULLISH" in direction:
            # 1. Structural Price Low of the Accumulation Shelf
            swing_low = float(recent_bars["low_unadj"].min())

            # 2. Anchored VWAP Floor over Lookback
            pv = (recent_bars["close_unadj"] * recent_bars["volume"]).sum()
            tot_vol = recent_bars["volume"].sum()
            avwap = pv / tot_vol if tot_vol > 0 else swing_low

            # Invalidation floor is anchored slightly below the swing low / accumulation shelf
            invalidation_price = round(min(swing_low, avwap * 0.98), 2)
            distance_pct = round(((current_price - invalidation_price) / current_price) * 100, 2)

            if current_price <= invalidation_price:
                status = "INVALIDATED (EXIT / THESIS VOID)"
            elif distance_pct <= 2.5:
                status = "WARNING: HIGH ALERT (Within 2.5% of Floor)"
            else:
                status = "STRUCTURALLY_SOUND"

            return {
                "invalidation_price": invalidation_price,
                "invalidation_type": "ACCUMULATION_SHELF_AND_AVWAP",
                "status": status,
                "distance_to_invalidation_pct": distance_pct,
                "swing_low": round(swing_low, 2),
                "anchored_vwap": round(avwap, 2)
            }
        else:
            # Bearish ceiling invalidation (break above recent resistance)
            swing_high = float(recent_bars["high_unadj"].max())
            invalidation_price = round(swing_high * 1.02, 2)
            distance_pct = round(((invalidation_price - current_price) / current_price) * 100, 2)

            if current_price >= invalidation_price:
                status = "INVALIDATED (SHORT COVER / THESIS VOID)"
            elif distance_pct <= 2.5:
                status = "WARNING: HIGH ALERT (Within 2.5% of Ceiling)"
            else:
                status = "STRUCTURALLY_SOUND"

            return {
                "invalidation_price": invalidation_price,
                "invalidation_type": "RESISTANCE_DISTRIBUTION_HIGH",
                "status": status,
                "distance_to_invalidation_pct": distance_pct,
                "swing_high": round(swing_high, 2)
            }

