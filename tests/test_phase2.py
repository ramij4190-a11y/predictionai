"""
Phase 2 Automated Test Suite.
Verifies Point-in-Time zero lookahead guard, promoter pledge detection, and announcement NLP scoring.
"""

from datetime import datetime, date, timedelta
import pandas as pd
import duckdb
from src.data.lakehouse import LakehouseManager
from src.fundamentals.bse_announcements import CorporateAnnouncementWatcher
from src.fundamentals.local_nlp import LocalNLPExtractor


def test_zero_lookahead_bias_guard():
    """
    CRITICAL TEST: Verify that the Point-in-Time lakehouse query strictly blocks
    quarterly results before their official regulatory filing timestamp.
    """
    lakehouse = LakehouseManager(db_path=":memory:")

    # Q3 Financials: Period ended 2024-12-31, but announced on 2025-02-14
    # Q2 Financials: Period ended 2024-09-30, announced on 2024-11-12
    records = [
        {
            "symbol": "TATAMOTORS",
            "period_end_date": date(2024, 9, 30),
            "filing_timestamp": datetime(2024, 11, 12, 18, 30),
            "revenue_cr": 105000.0,
            "ebitda_cr": 15000.0,
            "ebitda_margin_pct": 14.28,
            "pat_cr": 3500.0,
            "eps": 9.2,
            "debt_to_equity": 1.25,
            "promoter_holding_pct": 46.4,
            "pledged_promoter_pct": 0.0,
            "is_restated": False
        },
        {
            "symbol": "TATAMOTORS",
            "period_end_date": date(2024, 12, 31),
            "filing_timestamp": datetime(2025, 2, 14, 18, 30),
            "revenue_cr": 112000.0,
            "ebitda_cr": 17200.0,
            "ebitda_margin_pct": 15.35,
            "pat_cr": 4800.0,
            "eps": 12.5,
            "debt_to_equity": 1.15,
            "promoter_holding_pct": 46.4,
            "pledged_promoter_pct": 0.0,
            "is_restated": False
        }
    ]

    df = pd.DataFrame(records)
    lakehouse.insert_fundamentals(df)

    # 1. Backtest Simulation on 2025-01-15 (Before Q3 was released)
    # The backtester MUST NOT see Q3 data!
    df_jan = lakehouse.get_pit_fundamentals("TATAMOTORS", as_of_date="2025-01-15")
    assert len(df_jan) == 1, f"Expected exactly 1 statement, got {len(df_jan)}"
    assert pd.to_datetime(df_jan.iloc[0]["period_end_date"]).date() == date(2024, 9, 30), "Lookahead bias detected! Q3 was accessed before filing!"

    # 2. Backtest Simulation on 2025-02-20 (After Q3 was officially filed)
    # The backtester now sees both Q2 and Q3
    df_feb = lakehouse.get_pit_fundamentals("TATAMOTORS", as_of_date="2025-02-20")
    assert len(df_feb) == 2, f"Expected 2 statements, got {len(df_feb)}"
    assert pd.to_datetime(df_feb.iloc[-1]["period_end_date"]).date() == date(2024, 12, 31)

    lakehouse.close()
    print("[PASS] Zero lookahead bias audit: Future quarterly financials successfully blocked before filing date.")


def test_announcement_nlp_materiality_scoring():
    """Verify event classification and priority materiality scoring."""
    watcher = CorporateAnnouncementWatcher()
    nlp = LocalNLPExtractor()

    # Case 1: Promoter Pledge Alert
    headline_pledge = "Disclosure under Regulation 31(1) of SAST: Revocation of pledge on 2.4% promoter shares."
    score_pledge = watcher.score_announcement(headline_pledge, "Promoter Pledging")
    assert score_pledge["event_type"] == "PLEDGE_CHANGE"
    assert score_pledge["materiality_score"] >= 0.90

    nlp_pledge = nlp.extract_entities(headline_pledge)
    assert nlp_pledge["pledge_change_pct"] == -2.4, f"Expected -2.4% pledge revocation, got {nlp_pledge['pledge_change_pct']}"

    # Case 2: Order Win with Monetary Extraction
    headline_order = "Hindustan Aeronautics receives Letter of Award for supply of avionics worth Rs 2,800 Crores from Ministry of Defence."
    score_order = watcher.score_announcement(headline_order, "Order Win")
    assert score_order["event_type"] == "ORDER_WIN"
    assert score_order["materiality_score"] >= 0.85

    nlp_order = nlp.extract_entities(headline_order)
    assert nlp_order["monetary_value_inr_cr"] == 2800.0, f"Expected 2800 Cr, got {nlp_order['monetary_value_inr_cr']}"
    assert "Ministry of Defence" in str(nlp_order["counterparty"])

    # Case 3: Routine Compliance Filing (Low materiality)
    headline_routine = "Certificate under Regulation 74(5) of SEBI (DP) Regulations for the quarter ended December 31."
    score_routine = watcher.score_announcement(headline_routine, "Compliance Certificate")
    assert score_routine["event_type"] == "GENERAL"
    assert score_routine["materiality_score"] <= 0.30

    print("[PASS] Announcement scoring & NLP entity extraction passed.")


def test_duckdb_announcement_storage():
    """Verify storing and querying announcements in DuckDB."""
    lakehouse = LakehouseManager(db_path=":memory:")
    watcher = CorporateAnnouncementWatcher()

    items = [
        {
            "headline": "Outcome of Board Meeting: Unaudited Financial Results for Q2",
            "category": "Results",
            "announcement_timestamp": datetime(2025, 2, 10, 17, 30)
        },
        {
            "headline": "Compliance Certificate under Reg 7(3)",
            "category": "General",
            "announcement_timestamp": datetime(2025, 2, 9, 14, 0)
        }
    ]

    df_ann = watcher.parse_raw_announcements("RELIANCE", items)
    inserted = lakehouse.insert_announcements(df_ann)
    assert inserted == 2

    # Query with materiality filter >= 0.70 (should only return the Results announcement)
    df_high = lakehouse.get_recent_announcements("RELIANCE", min_materiality=0.70)
    assert len(df_high) == 1
    assert df_high.iloc[0]["event_type"] == "RESULTS"

    lakehouse.close()
    print("[PASS] DuckDB corporate announcement storage and materiality filtering passed.")


if __name__ == "__main__":
    print("\n--- Running Project Titan Phase 2 Test Suite ---")
    test_zero_lookahead_bias_guard()
    test_announcement_nlp_materiality_scoring()
    test_duckdb_announcement_storage()
    print("--- All Phase 2 Tests Passed Successfully! ---\n")
