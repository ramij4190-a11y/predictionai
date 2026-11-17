"""
Hidden Markov Model (HMM) Macro Regime Classifier.
Discovers latent liquidity states: Expansion (Bull), Compression (Bear/Shock), and Stagnation (Chop).
"""

from typing import Dict, Any, Tuple, List, Optional
import numpy as np
import pandas as pd
from hmmlearn.hmm import GaussianHMM
from src.data.lakehouse import LakehouseManager


class MacroRegimeClassifier:
    """Classifies market and macro regimes using Gaussian Hidden Markov Models."""

    REGIME_LABELS = {
        0: "EXPANSION (Bullish Liquidity)",
        1: "COMPRESSION (High-Risk Shock)",
        2: "STAGNATION (Range-Bound / Chop)"
    }

    def __init__(self, n_regimes: int = 3, random_state: int = 42):
        self.n_regimes = n_regimes
        self.model = GaussianHMM(
            n_components=n_regimes,
            covariance_type="full",
            n_iter=100,
            random_state=random_state
        )
        self.is_fitted = False
        self._state_mapping: Dict[int, int] = {}

    def prepare_regime_features(self, df_prices: pd.DataFrame, df_macro: pd.DataFrame) -> pd.DataFrame:
        """
        Assembles synchronized daily multi-variate feature matrix:
        1. Market 20-day return
        2. Market 20-day realized volatility
        3. Crude oil 20-day return
        4. USD/INR 20-day return
        """
        if df_prices.empty:
            return pd.DataFrame()

        # Compute benchmark price return & volatility
        p_pivot = df_prices.pivot(index="trade_date", columns="symbol", values="close_adj")
        market_return_20d = p_pivot.pct_change(20).mean(axis=1) * 100
        market_vol_20d = p_pivot.pct_change().rolling(20).std().mean(axis=1) * 100

        feat_df = pd.DataFrame({
            "market_ret_20d": market_return_20d,
            "market_vol_20d": market_vol_20d
        })

        # Add macro features if available
        if not df_macro.empty:
            m_pivot = df_macro.pivot(index="trade_date", columns="indicator_id", values="value")
            if "MACRO_BRENT_CRUDE" in m_pivot.columns:
                feat_df["crude_ret_20d"] = m_pivot["MACRO_BRENT_CRUDE"].pct_change(20) * 100
            if "MACRO_USDINR" in m_pivot.columns:
                feat_df["usdinr_ret_20d"] = m_pivot["MACRO_USDINR"].pct_change(20) * 100

        feat_df = feat_df.dropna()
        return feat_df

    def fit(self, features_df: pd.DataFrame) -> "MacroRegimeClassifier":
        """Fits Gaussian HMM on normalized multi-variate feature matrix."""
        if len(features_df) < 50:
            raise ValueError("Insufficient observations to train HMM regime model (minimum 50 required).")

        X = features_df.values
        self.model.fit(X)
        self.is_fitted = True

        # Sort states by volatility so state 0 is lowest volatility (Bull Expansion)
        # and state 1 is highest volatility (Bear Compression)
        vol_col_idx = 1 if features_df.shape[1] > 1 else 0
        state_vols = [self.model.means_[i][vol_col_idx] for i in range(self.n_regimes)]
        sorted_indices = np.argsort(state_vols)

        # Mapping: lowest vol -> 0, highest vol -> 1, middle vol -> 2
        self._state_mapping = {
            sorted_indices[0]: 0,  # Expansion
            sorted_indices[-1]: 1, # Compression
            sorted_indices[1]: 2   # Stagnation
        }
        return self

    def predict_regimes(self, features_df: pd.DataFrame) -> pd.Series:
        """Predicts latent regime for each date in the feature dataframe."""
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before predicting regimes.")

        raw_states = self.model.predict(features_df.values)
        mapped_states = [self._state_mapping.get(s, s) for s in raw_states]
        return pd.Series(mapped_states, index=features_df.index, name="regime_id")

    def get_current_regime(self, features_df: pd.DataFrame) -> Dict[str, Any]:
        """Returns the active regime, label, and state probabilities for the latest date."""
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before querying current regime.")

        latest_X = features_df.values[-1:]
        raw_state = self.model.predict(latest_X)[0]
        mapped_state = self._state_mapping.get(raw_state, raw_state)
        raw_probs = self.model.predict_proba(latest_X)[0]

        probs = {
            self.REGIME_LABELS[self._state_mapping.get(i, i)]: round(float(raw_probs[i]), 3)
            for i in range(self.n_regimes)
        }

        return {
            "regime_id": mapped_state,
            "regime_label": self.REGIME_LABELS.get(mapped_state, "UNKNOWN"),
            "confidence": round(float(np.max(raw_probs)), 3),
            "state_probabilities": probs,
            "as_of_date": str(features_df.index[-1])
        }

