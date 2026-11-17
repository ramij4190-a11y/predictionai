"""
Phase 5 Test Suite: Palantir Cockpit Backend & REST API Verification.
Validates all 10 endpoints, FastAPI routing table, schema integrity, and quantile monotonicity.
"""

import sys
from pathlib import Path
import time

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.backend.main import (
    app,
    get_system_status,
    get_universe_summary,
    refresh_universe_summary,
    get_stock_history,
    get_stock_corridor,
    get_stock_analog,
    get_stock_ontology,
    get_stock_fundamentals,
    get_macro_regime,
    get_announcements,
    serve_index,
)


def test_fastapi_route_registry():
    """Verify that all REST endpoints are formally registered on the FastAPI app."""
    routes = [route.path for route in app.routes]
    expected_routes = [
        "/api/v1/system/status",
        "/api/v1/universe/summary",
        "/api/v1/universe/refresh",
        "/api/v1/stocks/{symbol}/history",
        "/api/v1/stocks/{symbol}/corridor",
        "/api/v1/stocks/{symbol}/analog",
        "/api/v1/stocks/{symbol}/ontology",
        "/api/v1/stocks/{symbol}/fundamentals",
        "/api/v1/macro/regime",
        "/api/v1/announcements",
        "/",
    ]
    for r in expected_routes:
        assert r in routes, f"Missing expected route in FastAPI registry: {r}"
    print(f"[PASS] FastAPI route table verified ({len(expected_routes)} endpoints registered).", flush=True)


def test_system_status():
    """Verify system telemetry status."""
    data = get_system_status()
    assert data["status"] == "OPERATIONAL"
    assert data["duckdb_connected"] is True
    assert data["total_daily_bars"] >= 60000
    assert data["models_loaded"]["directional_classifier"] is True
    assert data["models_loaded"]["quantile_corridors"] is True
    assert data["models_loaded"]["macro_regime_hmm"] is True
    print(f"[PASS] System status verified ({data['total_daily_bars']} bars, query latency: {data['query_latency_ms']}ms).", flush=True)


def test_universe_summary():
    """Verify 50-stock universe matrix schema and values."""
    t0 = time.time()
    summary = get_universe_summary()
    latency_ms = (time.time() - t0) * 1000

    assert len(summary) == 50, f"Expected 50 stocks in universe summary, got {len(summary)}"

    first = summary[0]
    expected_fields = [
        "symbol", "company_name", "sector", "current_price",
        "change_20d_pct", "directional_tilt", "confidence_score_pct",
        "projected_median_price", "bearish_floor_price_q05", "bullish_ceiling_price_q95",
        "invalidation_floor", "thesis_status", "distance_to_invalidation_pct"
    ]
    for field in expected_fields:
        assert field in first, f"Missing required field '{field}' in universe summary"

    assert first["current_price"] > 0
    assert first["directional_tilt"] in ["BULLISH", "BEARISH", "NEUTRAL"]
    print(f"[PASS] 50-stock universe matrix verified ({len(summary)} stocks retrieved in {latency_ms:.2f}ms).", flush=True)


def test_stock_history():
    """Verify candlestick and volume bar series formatted for TradingView Lightweight Charts."""
    data = get_stock_history("TATAMOTORS")
    assert data["symbol"] == "TATAMOTORS"
    assert len(data["candles"]) > 500
    assert len(data["volumes"]) == len(data["candles"])

    candle = data["candles"][0]
    assert "time" in candle
    assert "open" in candle
    assert "high" in candle
    assert "low" in candle
    assert "close" in candle
    assert candle["high"] >= candle["low"]
    print(f"[PASS] TradingView candlestick series verified ({len(data['candles'])} bars).", flush=True)


def test_stock_corridor():
    """Verify 60-day quantile corridor and non-crossing monotonicity."""
    data = get_stock_corridor("TATAMOTORS")
    assert data["symbol"] == "TATAMOTORS"
    assert data["current_price"] > 0
    assert "invalidation_floor" in data
    assert "q05_floor" in data
    assert "q50_median" in data
    assert "q95_ceiling" in data

    # Verify non-crossing corridor ordering: q05 <= q50 <= q95
    assert data["q05_floor"] <= data["q50_median"] <= data["q95_ceiling"], \
        f"Quantile crossing detected: {data['q05_floor']} <= {data['q50_median']} <= {data['q95_ceiling']}"

    assert len(data["median_series"]) > 0
    assert len(data["upper_series"]) == len(data["median_series"])
    assert len(data["lower_series"]) == len(data["median_series"])
    print(f"[PASS] Non-crossing quantile corridor verified (q05: ₹{data['q05_floor']} <= q50: ₹{data['q50_median']} <= q95: ₹{data['q95_ceiling']}).", flush=True)


def test_stock_analog():
    """Verify FastDTW pattern analogy retrieval."""
    analogs = get_stock_analog("TATAMOTORS")
    assert isinstance(analogs, list)
    assert len(analogs) <= 3
    if analogs:
        first = analogs[0]
        assert "match_date" in first
        assert "similarity_score" in first
        assert "subsequent_6m_return_pct" in first
        assert 0.0 <= first["similarity_score"] <= 1.0
    print(f"[PASS] FastDTW historical analogies verified ({len(analogs)} episodes found).", flush=True)


def test_stock_ontology():
    """Verify localized ego-network for Cytoscape.js canvas."""
    data = get_stock_ontology("TATAMOTORS")
    assert data["symbol"] == "TATAMOTORS"
    assert "nodes" in data
    assert "edges" in data
    assert len(data["nodes"]) > 0
    assert len(data["edges"]) > 0

    node_ids = [n["id"] for n in data["nodes"]]
    assert "TATAMOTORS" in node_ids
    print(f"[PASS] Cytoscape.js ego-network verified ({len(data['nodes'])} nodes, {len(data['edges'])} edges).", flush=True)


def test_stock_fundamentals():
    """Verify Point-in-Time quarterly financials."""
    funds = get_stock_fundamentals("TATAMOTORS")
    assert isinstance(funds, list)
    if funds:
        latest = funds[0]
        assert "filing_timestamp" in latest
        assert "revenue_cr" in latest
        assert "ebitda_margin_pct" in latest
        assert "debt_to_equity" in latest
    print(f"[PASS] Point-in-Time fundamentals verified ({len(funds)} quarterly filings).", flush=True)


def test_macro_regime():
    """Verify HMM macro regime classification and macro variables."""
    data = get_macro_regime()
    assert "regime" in data
    assert "indicators" in data
    regime = data["regime"]
    assert "regime_id" in regime
    assert "regime_label" in regime
    assert "confidence" in regime
    print(f"[PASS] Macro HMM regime verified (Active: {regime['regime_label']}, Confidence: {regime['confidence'] * 100:.1f}%).", flush=True)


def test_announcements():
    """Verify BSE corporate announcements with NLP entity extracts."""
    announcements = get_announcements()
    assert isinstance(announcements, list)
    assert len(announcements) > 0

    first = announcements[0]
    assert "announcement_id" in first
    assert "symbol" in first
    assert "materiality_score" in first
    assert "headline" in first
    print(f"[PASS] BSE announcements verified ({len(announcements)} disclosures tracked).", flush=True)


def test_static_index():
    """Verify root HTML dashboard template exists and is properly served."""
    response = serve_index()
    index_path = Path(response.path)
    assert index_path.exists()
    content = index_path.read_text(encoding="utf-8")
    assert "TITAN PALANTIR COCKPIT" in content
    assert "lightweight-charts.standalone.production.js" in content
    assert "cytoscape.min.js" in content
    print(f"[PASS] Static single-page interface verified ({index_path.name} configured with offline vendor JS).", flush=True)


if __name__ == "__main__":
    print("\n=======================================================", flush=True)
    print("   PROJECT TITAN - PHASE 5 PALANTIR COCKPIT TEST SUITE ", flush=True)
    print("=======================================================", flush=True)
    test_fastapi_route_registry()
    test_system_status()
    test_universe_summary()
    test_stock_history()
    test_stock_corridor()
    test_stock_analog()
    test_stock_ontology()
    test_stock_fundamentals()
    test_macro_regime()
    test_announcements()
    test_static_index()
    print("=======================================================", flush=True)
    print("   ALL PHASE 5 TESTS PASSED WITH 100% SUCCESS!        ", flush=True)
    print("=======================================================\n", flush=True)
