"""
Macro-Conditioned FastDTW Historical Pattern Analogy Engine.
Matches current 60-day consolidation/accumulation patterns against 5+ years of historical market episodes.
"""

from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean


class HistoricalAnalogyMatcher:
    """Discovers structural chart and macro analogs using Dynamic Time Warping (DTW)."""

    def __init__(self, window_size: int = 60, forward_horizon: int = 126):
        """
        window_size: Length of current pattern to match (e.g. 60 trading days ~ 3 months)
        forward_horizon: Subsequent period to evaluate outcomes (e.g. 126 trading days ~ 6 months)
        """
        self.window_size = window_size
        self.forward_horizon = forward_horizon

    def _normalize_series(self, series: np.ndarray) -> np.ndarray:
        """Applies Min-Max scaling to isolate shape from nominal price level."""
        s_min = np.min(series)
        s_max = np.max(series)
        if s_max - s_min == 0:
            return np.zeros_like(series)
        return (series - s_min) / (s_max - s_min)

    def find_top_analogs(
        self,
        symbol: str,
        df_bars: pd.DataFrame,
        macro_vector_curr: Optional[np.ndarray] = None,
        top_k: int = 3,
        step_stride: int = 15
    ) -> List[Dict[str, Any]]:
        """
        Finds top K historical pattern matches in df_bars for the specified symbol.
        df_bars must contain: ['trade_date', 'close_adj'] sorted chronologically.
        """
        if len(df_bars) < (self.window_size + self.forward_horizon + 30):
            return []

        prices = df_bars["close_adj"].values
        dates = df_bars["trade_date"].values

        # Current lookback window
        current_window = prices[-self.window_size:]
        curr_norm = self._normalize_series(current_window)

        analogs = []
        # Search candidate historical windows (leave buffer so forward outcome is fully known)
        max_start_idx = len(prices) - self.window_size - self.forward_horizon

        for start_idx in range(0, max_start_idx, step_stride):
            end_idx = start_idx + self.window_size
            candidate_window = prices[start_idx:end_idx]
            cand_norm = self._normalize_series(candidate_window)

            # 1. Compute FastDTW Shape Distance (scalar-safe absolute difference)
            dtw_dist, _ = fastdtw(curr_norm, cand_norm, dist=lambda a, b: abs(a - b))
            # Normalize DTW distance by length
            norm_dtw = dtw_dist / self.window_size

            # 2. Total composite distance (bounded between 0.0 to 1.0 similarity)
            composite_dist = norm_dtw
            similarity_score = max(0.0, round(1.0 - (composite_dist / 1.5), 3))

            # 3. Calculate subsequent forward outcome over 6 months
            forward_prices = prices[end_idx : end_idx + self.forward_horizon]
            if len(forward_prices) == 0:
                continue

            entry_price = candidate_window[-1]
            subsequent_return = round(((forward_prices[-1] - entry_price) / entry_price) * 100, 2)
            max_rally = round(((np.max(forward_prices) - entry_price) / entry_price) * 100, 2)
            max_drawdown = round(((np.min(forward_prices) - entry_price) / entry_price) * 100, 2)

            match_date = str(dates[end_idx - 1])

            analogs.append({
                "symbol": symbol.upper(),
                "match_date": match_date,
                "similarity_score": similarity_score,
                "composite_distance": round(composite_dist, 4),
                "subsequent_6m_return_pct": subsequent_return,
                "subsequent_6m_max_rally_pct": max_rally,
                "subsequent_6m_max_drawdown_pct": max_drawdown
            })

        # Sort by smallest distance / highest similarity
        ranked_analogs = sorted(analogs, key=lambda x: x["composite_distance"])
        return ranked_analogs[:top_k]
