"""
Phase 1 Automated Test Suite.
Verifies universe configuration, DuckDB schema, corporate action adjustment math, and query latency.
"""

import time
from datetime import datetime, timedelta
import pandas as pd
import duckdb
from src.data.universe import UniverseManager
from src.data.lakehouse import LakehouseManager
from src.data.corporate_actions import CorporateActionAdjuster


def test_universe_loading():
    """Verify all 50 Indian equities are correctly configured with valid metadata."""
    mgr = UniverseManager()
    equities = mgr.get_all()
    assert len(equities) == 50, f"Expected 50 equities, found {len(equities)}"
    
    # Check key anchor stocks
    tatamotors = mgr.get_by_symbol("TATAMOTORS")
    assert tatamotors is not None
    assert tatamotors.bse_code == "500570"
    assert tatamotors.sector == "Automotive"

    reliance = mgr.get_by_symbol("RELIANCE")
    assert reliance is not None
    assert reliance.bse_code == "500325"

    sectors = mgr.get_sectors()
    assert len(sectors) >= 8, f"Expected diverse sectors, found {len(sectors)}"
    print("[PASS] Universe loading & 50-stock schema validation.")


def test_corporate_action_split_adjustment():
    """
    Verify that a 2:1 stock split on date T correctly back-adjusts
    pre-split prices so no artificial -50% price cliff occurs in close_adj.
    """
    # Create synthetic price series: 10 trading days
    # Day 0 to 4: Traded around 1000.00
    # Day 5 (Ex-Date): 2:1 Split occurred, stock now trades around 500.00
    dates = [datetime(2025, 1, 1).date() + timedelta(days=i) for i in range(10)]
    prices = [1000.0, 1010.0, 990.0, 1005.0, 1020.0, 510.0, 515.0, 520.0, 518.0, 525.0]

    df_synthetic = pd.DataFrame({
        "trade_date": dates,
        "open_unadj": prices,
        "high_unadj": [p + 10 for p in prices],
        "low_unadj": [p - 10 for p in prices],
        "close_unadj": prices,
        "volume": [100000] * 10
    })

    actions = [{
        "action_id": "SPLIT_20250106",
        "symbol": "MOCKSTOCK",
        "ex_date": str(dates[5]),  # Day 5 is ex-date
        "action_type": "SPLIT",
        "ratio_from": 1.0,
        "ratio_to": 2.0,
        "adjustment_factor": 0.5  # Pre-split prices must be multiplied by 0.5
    }]

    df_adjusted = CorporateActionAdjuster.adjust_series(df_synthetic, actions)

    # 1. Unadjusted series on Day 4 and Day 5 reflects nominal traded prices (1020 -> 510)
    assert df_adjusted.loc[4, "close_unadj"] == 1020.0
    assert df_adjusted.loc[5, "close_unadj"] == 510.0

    # 2. Adjusted series on Day 4 was scaled by 0.5 (1020 * 0.5 = 510)
    assert df_adjusted.loc[4, "close_adj"] == 510.0
    assert df_adjusted.loc[5, "close_adj"] == 510.0

    # 3. Calculate 1-day return between Day 4 and Day 5
    # Unadjusted return would erroneously be -50%!
    # Adjusted return is (510 - 510) / 510 = 0.0% (smooth economic continuity)
    ret_adj = (df_adjusted.loc[5, "close_adj"] - df_adjusted.loc[4, "close_adj"]) / df_adjusted.loc[4, "close_adj"]
    assert abs(ret_adj) < 0.01, f"Expected 0% economic drop across split, got {ret_adj}"
    print("[PASS] Corporate action split adjustment correctly eliminates price cliffs.")


def test_duckdb_lakehouse_operations():
    """Verify DuckDB table creation, batch insertion, and query latency benchmark."""
    # Use in-memory DuckDB instance for high-speed isolated test
    conn = duckdb.connect(database=":memory:")
    lakehouse = LakehouseManager(db_path=":memory:")

    universe_mgr = UniverseManager()
    equities = universe_mgr.get_all()

    # 1. Test Seed Universe
    count = lakehouse.seed_universe(equities)
    assert count == 50

    # 2. Insert synthetic 5-year daily series for 5 stocks
    sample_symbols = ["TATAMOTORS", "RELIANCE", "INFY", "HDFCBANK", "TCS"]
    dfs = []
    base_date = datetime(2020, 1, 1).date()

    for sym in sample_symbols:
        n_days = 1250  # ~5 years of trading days
        df_sym = pd.DataFrame({
            "symbol": [sym] * n_days,
            "trade_date": [base_date + timedelta(days=i) for i in range(n_days)],
            "open_unadj": [500.0 + (i * 0.1) for i in range(n_days)],
            "high_unadj": [510.0 + (i * 0.1) for i in range(n_days)],
            "low_unadj": [490.0 + (i * 0.1) for i in range(n_days)],
            "close_unadj": [505.0 + (i * 0.1) for i in range(n_days)],
            "volume": [250000] * n_days,
            "close_adj": [505.0 + (i * 0.1) for i in range(n_days)],
            "delivery_qty": [125000] * n_days,
            "delivery_pct": [50.0] * n_days,
            "turnover_cr": [12.5] * n_days
        })
        dfs.append(df_sym)

    df_all = pd.concat(dfs, ignore_index=True)
    inserted = lakehouse.insert_daily_bars(df_all)
    assert inserted == len(df_all)

    # 3. Benchmark Query Latency (< 100ms)
    t0 = time.time()
    series = lakehouse.get_daily_series("TATAMOTORS", "2021-01-01", "2024-01-01")
    query_ms = (time.time() - t0) * 1000
    
    assert not series.empty
    assert query_ms < 100.0, f"Query took {query_ms:.2f}ms, expected < 100ms"

    # 4. Market Summary Aggregation
    summary = lakehouse.get_market_summary()
    assert not summary.empty
    assert len(summary) == 5

    lakehouse.close()
    print(f"[PASS] DuckDB Lakehouse operations passed (Query latency: {query_ms:.2f}ms).")


if __name__ == "__main__":
    print("\n--- Running Project Titan Phase 1 Test Suite ---")
    test_universe_loading()
    test_corporate_action_split_adjustment()
    test_duckdb_lakehouse_operations()
    print("--- All Phase 1 Tests Passed Successfully! ---\n")

