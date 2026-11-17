"""
Probabilistic Quantile Corridor Engine.
Forecasts non-parametric uncertainty ribbons (5%, 50%, 95% quantiles) over 2-to-8-month forward horizons.
"""

from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
import lightgbm as lgb


class QuantileCorridorRegressor:
    """Trains Pinball Loss Quantile Regressors for multi-horizon uncertainty corridors."""

    FEATURE_COLS = [
        "ret_20d", "ret_60d", "dist_sma50", "dist_sma200",
        "rsi_14", "volatility_20d", "delivery_ratio", "dist_vwap60",
        "ebitda_margin_pct", "debt_to_equity", "graph_shock_score"
    ]

    QUANTILES = [0.05, 0.50, 0.95]

    def __init__(self, random_state: int = 42):
        self.models: Dict[float, lgb.LGBMRegressor] = {}
        self.is_fitted = False
        self.random_state = random_state

    def fit(self, df_dataset: pd.DataFrame, target_col: str = "fwd_ret_60d") -> "QuantileCorridorRegressor":
        """
        Trains 3 distinct quantile regressors optimizing Pinball Loss for 5%, 50%, 95%.
        """
        df_valid = df_dataset.dropna(subset=[target_col]).reset_index(drop=True)
        if len(df_valid) < 100:
            raise ValueError(f"Insufficient samples for quantile regression: {len(df_valid)}")

        X = df_valid[self.FEATURE_COLS]
        y = df_valid[target_col]

        for q in self.QUANTILES:
            model_q = lgb.LGBMRegressor(
                objective="quantile",
                alpha=q,
                n_estimators=80,
                learning_rate=0.03,
                max_depth=4,
                num_leaves=15,
                subsample=0.8,
                random_state=self.random_state,
                verbose=-1
            )
            model_q.fit(X, y)
            self.models[q] = model_q

        self.is_fitted = True
        return self

    def project_corridor(
        self, 
        latest_row: pd.DataFrame, 
        current_price: float, 
        horizon_days: int = 60
    ) -> Dict[str, Any]:
        """
        Projects future price boundaries for the next horizon_days.
        Enforces non-crossing quantile monotonicity: q05 <= q50 <= q95.
        """
        if not self.is_fitted:
            raise RuntimeError("Models must be fitted before generating corridor.")

        X_row = latest_row[self.FEATURE_COLS].iloc[-1:]

        raw_returns = {
            q: float(self.models[q].predict(X_row)[0])
            for q in self.QUANTILES
        }

        # Monotonicity check (guarantee q05 <= q50 <= q95)
        sorted_rets = sorted(raw_returns.values())
        ret_05 = sorted_rets[0]
        ret_50 = sorted_rets[1]
        ret_95 = sorted_rets[2]

        price_floor = round(current_price * (1.0 + ret_05), 2)
        price_median = round(current_price * (1.0 + ret_50), 2)
        price_ceiling = round(current_price * (1.0 + ret_95), 2)

        return {
            "current_price": round(current_price, 2),
            "horizon_trading_days": horizon_days,
            "projected_median_price": price_median,
            "projected_median_return_pct": round(ret_50 * 100, 2),
            "bullish_ceiling_price_q95": price_ceiling,
            "bullish_ceiling_return_pct": round(ret_95 * 100, 2),
            "bearish_floor_price_q05": price_floor,
            "bearish_floor_return_pct": round(ret_05 * 100, 2),
            "corridor_width_pct": round((ret_95 - ret_05) * 100, 2)
        }

