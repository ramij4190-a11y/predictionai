"""
Phase 3 Automated Test Suite.
Verifies Graph Ontology integrity, Network Spillover shock diffusion, HMM regime classification, and FastDTW pattern analogies.
"""

from datetime import datetime, date, timedelta
import numpy as np
import pandas as pd
from src.graph.ontology_builder import MarketGraphOntology
from src.graph.spillover_engine import NetworkSpilloverEngine
from src.macro.regime_classifier import MacroRegimeClassifier
from src.analytics.pattern_analogy import HistoricalAnalogyMatcher


def test_graph_ontology_and_ego_network():
    """Verify graph creation, node counts, and localized ego-network scoping."""
    ontology = MarketGraphOntology()
    g = ontology.graph

    # 1. Total Node and Edge Counts
    assert g.number_of_nodes() >= 60, f"Expected >= 60 nodes, got {g.number_of_nodes()}"
    assert g.has_node("TATAMOTORS")
    assert g.has_node("RELIANCE")
    assert g.has_node("MACRO_BRENT_CRUDE")
    assert g.has_node("GRP_TATA")

    # 2. Check Relationship Edges
    assert g.has_edge("BHARATFORG", "TATAMOTORS"), "Missing supply chain edge BHARATFORG -> TATAMOTORS"
    assert g.has_edge("MACRO_BRENT_CRUDE", "ASIANPAINT"), "Missing raw material edge BRENT_CRUDE -> ASIANPAINT"

    # 3. Test Ego-Network Scoping (Hairball Elimination)
    ego_data = ontology.get_ego_network("TATAMOTORS", max_hops=1)
    ego_nodes = ego_data["nodes"]
    ego_edges = ego_data["edges"]

    # In 1-hop radius, TATAMOTORS should only see its direct suppliers, group, and sector (under 15 nodes)
    assert 3 <= len(ego_nodes) <= 15, f"Expected 3-15 localized ego nodes, got {len(ego_nodes)}"
    node_ids = [n["id"] for n in ego_nodes]
    assert "TATAMOTORS" in node_ids
    assert "BHARATFORG" in node_ids  # Direct supplier
    assert "ZOMATO" not in node_ids  # Unrelated company must be filtered out!

    print("[PASS] Graph ontology & localized ego-network scoping passed.")


def test_spillover_shock_diffusion():
    """Verify raw material shock diffusion and downstream margin pressure calculations."""
    ontology = MarketGraphOntology()
    spillover = NetworkSpilloverEngine(ontology.graph)

    # Simulate +20% Crude Oil spike, +15% Steel spike, +5% USDINR depreciation
    shock = {
        "MACRO_BRENT_CRUDE": 0.20,
        "MACRO_DOMESTIC_STEEL": 0.15,
        "MACRO_USDINR": 0.05
    }
    impacts = spillover.simulate_macro_shock(shock)

    # 1. Asian Paints should experience heavy margin squeeze from crude (0.20 * -0.45 = -0.09)
    assert "ASIANPAINT" in impacts
    assert impacts["ASIANPAINT"] == -0.09, f"Expected -0.09 impact on ASIANPAINT, got {impacts['ASIANPAINT']}"

    # 2. TCS should benefit from INR depreciation (0.05 * 0.35 = +0.0175)
    assert "TCS" in impacts
    assert impacts["TCS"] == 0.0175, f"Expected +0.0175 impact on TCS, got {impacts['TCS']}"

    # 3. Tata Motors should experience both direct steel pressure and second-order supplier pressure
    assert "TATAMOTORS" in impacts
    assert impacts["TATAMOTORS"] < 0.0, "Tata Motors should experience negative cost pressure from steel spike"

    print("[PASS] Supply chain spillover & shock diffusion simulation passed.")


def test_hmm_macro_regime_classifier():
    """Verify unsupervised regime clustering using synthetic market states."""
    clf = MacroRegimeClassifier(n_regimes=3, random_state=42)

    # Generate 150 synthetic days:
    # Days 0-49: Steady bull expansion (positive return, low volatility)
    # Days 50-99: Bear crash / high shock (negative return, high volatility)
    # Days 100-149: Range-bound consolidation (zero return, moderate volatility)
    np.random.seed(42)
    bull_ret = np.random.normal(loc=12.0, scale=2.0, size=50)
    bull_vol = np.random.normal(loc=1.0, scale=0.2, size=50)

    bear_ret = np.random.normal(loc=-18.0, scale=4.0, size=50)
    bear_vol = np.random.normal(loc=4.5, scale=0.5, size=50)

    chop_ret = np.random.normal(loc=0.5, scale=1.5, size=50)
    chop_vol = np.random.normal(loc=2.2, scale=0.3, size=50)

    dates = [date(2025, 1, 1) + timedelta(days=i) for i in range(150)]
    df_features = pd.DataFrame({
        "market_ret_20d": np.concatenate([bull_ret, bear_ret, chop_ret]),
        "market_vol_20d": np.concatenate([bull_vol, bear_vol, chop_vol])
    }, index=dates)

    clf.fit(df_features)
    regimes = clf.predict_regimes(df_features)

    assert len(regimes) == 150
    assert set(regimes.unique()).issubset({0, 1, 2})

    current = clf.get_current_regime(df_features)
    assert "regime_id" in current
    assert "regime_label" in current
    assert current["confidence"] >= 0.50
    assert sum(current["state_probabilities"].values()) > 0.99

    print("[PASS] Gaussian HMM regime discovery & probability estimation passed.")


def test_fastdtw_pattern_analogy():
    """Verify FastDTW structural pattern matching and forward outcome tracking."""
    matcher = HistoricalAnalogyMatcher(window_size=30, forward_horizon=60)

    # Create synthetic series of 250 days with two identical U-shaped accumulation patterns
    dates = [date(2024, 1, 1) + timedelta(days=i) for i in range(250)]
    # Base pattern: 30 days U-shape
    u_shape = np.array([100 - (15 - abs(i - 15)) for i in range(30)])

    prices = np.ones(250) * 100.0
    # Place historical U-shape at index 20..50, followed by a 40% rally
    prices[20:50] = u_shape
    prices[50:110] = np.linspace(100.0, 140.0, 60)

    # Place identical U-shape at the very end (index 220..250)
    prices[220:250] = u_shape

    df_synthetic = pd.DataFrame({
        "trade_date": dates,
        "close_adj": prices
    })

    analogs = matcher.find_top_analogs("MOCKSTOCK", df_synthetic, top_k=1, step_stride=5)

    assert len(analogs) == 1
    match = analogs[0]
    # The historical U-shape at index 20..50 should be recognized with high similarity
    assert match["similarity_score"] >= 0.80, f"Expected similarity >= 80%, got {match['similarity_score']}"
    assert 38.0 <= match["subsequent_6m_return_pct"] <= 45.0, f"Expected ~40% subsequent rally, got {match['subsequent_6m_return_pct']}"

    print("[PASS] FastDTW pattern analogy & forward outcome calculation passed.")


if __name__ == "__main__":
    print("\n--- Running Project Titan Phase 3 Test Suite ---")
    test_graph_ontology_and_ego_network()
    test_spillover_shock_diffusion()
    test_hmm_macro_regime_classifier()
    test_fastdtw_pattern_analogy()
    print("--- All Phase 3 Tests Passed Successfully! ---\n")
