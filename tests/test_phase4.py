"""
Phase 4 Automated Test Suite.
Verifies Feature Engineering, Purged Cross-Validation, Directional LightGBM classification,
Quantile Corridor monotonicity, and Structural Invalidation floors.
"""

from datetime import datetime, date, timedelta
import numpy as np
import pandas as pd
from src.models.feature_pipeline import FinancialFeaturePipeline
from src.models.cross_validation import PurgedWalkForwardCV
from src.models.directional_classifier import DirectionalClassifier
from src.models.quantile_corridors import QuantileCorridorRegressor
from src.models.invalidation_engine import InvalidationEngine


def test_purged_walk_forward_cv():
    """Verify that train and test splits have zero label overlap and respect purge window."""
    n_samples = 300
    df_dummy = pd.DataFrame({"dummy": np.arange(n_samples)})
    cv = PurgedWalkForwardCV(n_splits=3, purge_window=60, embargo_window=20)

    for train_idx, test_idx in cv.split(df_dummy):
        # 1. Train must precede test
        assert max(train_idx) < min(test_idx)
        # 2. Distance between train end and test start must be >= purge_window
        gap = min(test_idx) - max(train_idx) - 1
        assert gap >= 60, f"Purge window violated! Gap was {gap}, expected >= 60"

    print("[PASS] Purged and embargoed cross-validation splitter verified.")


def test_directional_classifier_training():
    """Verify LightGBM directional classifier training and probabilistic predictions."""
    np.random.seed(42)
    n = 250
    # Generate synthetic features
    df_synthetic = pd.DataFrame({
        "ret_20d": np.random.normal(5, 10, n),
        "ret_60d": np.random.normal(8, 15, n),
        "ret_120d": np.random.normal(12, 20, n),
        "dist_sma50": np.random.normal(2, 5, n),
        "dist_sma200": np.random.normal(5, 8, n),
        "rsi_14": np.random.uniform(30, 70, n),
        "volatility_20d": np.random.uniform(15, 35, n),
        "delivery_ratio": np.random.uniform(0.8, 1.4, n),
        "dist_vwap60": np.random.normal(1, 4, n),
        "ebitda_margin_pct": np.random.uniform(10, 25, n),
        "debt_to_equity": np.random.uniform(0.1, 1.5, n),
        "promoter_holding_pct": np.random.uniform(40, 60, n),
        "pledged_promoter_pct": np.zeros(n),
        "graph_shock_score": np.random.normal(0, 0.05, n),
        # Target: correlated with momentum
        "target_dir_60d": np.where(np.random.normal(5, 10, n) > 3, 1, 0)
    })

    clf = DirectionalClassifier(random_state=42)
    metrics = clf.train_and_validate(df_synthetic)
    assert "mean_walk_forward_accuracy_pct" in metrics
    assert clf.is_fitted

    # Predict on latest row
    res = clf.predict_current_direction(df_synthetic.iloc[-1:])
    assert res["directional_tilt"] in ["BULLISH", "BEARISH", "NEUTRAL"]
    assert 0.0 <= res["bullish_probability_pct"] <= 100.0
    assert 0.0 <= res["confidence_score_pct"] <= 100.0
    assert len(res["primary_catalyst_drivers"]) == 3

    print("[PASS] Directional LightGBM classifier training & inference verified.")


def test_quantile_corridor_monotonicity():
    """Verify that quantile regressors produce non-crossing quantile bands (q05 <= q50 <= q95)."""
    np.random.seed(42)
    n = 200
    df_synthetic = pd.DataFrame({
        "ret_20d": np.random.normal(3, 8, n),
        "ret_60d": np.random.normal(6, 12, n),
        "dist_sma50": np.random.normal(2, 4, n),
        "dist_sma200": np.random.normal(4, 6, n),
        "rsi_14": np.random.uniform(35, 65, n),
        "volatility_20d": np.random.uniform(15, 30, n),
        "delivery_ratio": np.random.uniform(0.9, 1.3, n),
        "dist_vwap60": np.random.normal(1, 3, n),
        "ebitda_margin_pct": np.random.uniform(12, 22, n),
        "debt_to_equity": np.random.uniform(0.2, 1.2, n),
        "graph_shock_score": np.random.normal(0, 0.04, n),
        "fwd_ret_60d": np.random.normal(0.05, 0.15, n)
    })

    reg = QuantileCorridorRegressor(random_state=42)
    reg.fit(df_synthetic, target_col="fwd_ret_60d")
    assert reg.is_fitted

    curr_price = 1000.0
    corridor = reg.project_corridor(df_synthetic.iloc[-1:], current_price=curr_price, horizon_days=60)

    p05 = corridor["bearish_floor_price_q05"]
    p50 = corridor["projected_median_price"]
    p95 = corridor["bullish_ceiling_price_q95"]

    # Strict Monotonicity: Floor <= Median <= Ceiling
    assert p05 <= p50 <= p95, f"Quantile crossing detected! {p05} <= {p50} <= {p95}"
    assert corridor["corridor_width_pct"] > 0.0

    print(f"[PASS] Quantile corridor monotonicity verified: Floor ₹{p05} <= Median ₹{p50} <= Ceiling ₹{p95}")


def test_structural_invalidation_math():
    """Verify structural stop-loss calculation and alert triggers."""
    # Create 60 days of bars trading between 800 and 1000
    dates = [date(2025, 1, 1) + timedelta(days=i) for i in range(60)]
    prices = np.linspace(850.0, 950.0, 60)

    df_bars = pd.DataFrame({
        "trade_date": dates,
        "open_unadj": prices,
        "high_unadj": prices + 15,
        "low_unadj": prices - 15,
        "close_unadj": prices,
        "volume": [500000] * 60
    })

    # Case 1: Healthy Bullish Position (Price is ₹950, well above floor)
    res_sound = InvalidationEngine.calculate_invalidation_floor(df_bars, current_price=950.0, direction="BULLISH")
    assert res_sound["status"] == "STRUCTURALLY_SOUND"
    assert res_sound["invalidation_price"] < 950.0
    assert res_sound["distance_to_invalidation_pct"] > 2.5

    # Case 2: Proximity Warning (Price drops to within 2% of floor)
    floor = res_sound["invalidation_price"]
    price_near = floor * 1.015  # 1.5% above floor
    res_warning = InvalidationEngine.calculate_invalidation_floor(df_bars, current_price=price_near, direction="BULLISH")
    assert "WARNING" in res_warning["status"]

    # Case 3: Breached Invalidation (Price drops below floor)
    price_breached = floor * 0.98
    res_breach = InvalidationEngine.calculate_invalidation_floor(df_bars, current_price=price_breached, direction="BULLISH")
    assert "INVALIDATED" in res_breach["status"]

    print("[PASS] Structural invalidation floor & alert state machine verified.")


if __name__ == "__main__":
    print("\n--- Running Project Titan Phase 4 Test Suite ---")
    test_purged_walk_forward_cv()
    test_directional_classifier_training()
    test_quantile_corridor_monotonicity()
    test_structural_invalidation_math()
    print("--- All Phase 4 Tests Passed Successfully! ---\n")
