"""
BSE & NSE Corporate Announcement Ingestion & Materiality Scoring Engine.
Parses corporate announcements, detects material events, and assigns priority scores.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, date
import re
import hashlib
import pandas as pd
import httpx


class CorporateAnnouncementWatcher:
    """Ingests and scores corporate disclosures for Indian equities."""

    # High-impact regex patterns for event classification
    EVENT_RULES = [
        {
            "event_type": "PLEDGE_CHANGE",
            "regex": r"(pledg|encumbrance|revocation of pledg|release of shares)",
            "base_score": 0.95
        },
        {
            "event_type": "RESULTS",
            "regex": r"(financial results|outcome of board meeting|audited results|unaudited results|quarterly results)",
            "base_score": 0.90
        },
        {
            "event_type": "GOVERNANCE_ALERT",
            "regex": r"(resignation of (auditor|statutory auditor|director|cfo|ceo|managing director)|investigation|search and seizure)",
            "base_score": 0.95
        },
        {
            "event_type": "ORDER_WIN",
            "regex": r"(bagged order|order win|receipt of order|letter of award|commercial contract|awarded contract)",
            "base_score": 0.85
        },
        {
            "event_type": "CAPEX_EXPANSION",
            "regex": r"(capacity expansion|new plant|commercial production|commissioning of|capex)",
            "base_score": 0.80
        },
        {
            "event_type": "DIVIDEND_BONUS",
            "regex": r"(recommendation of dividend|interim dividend|bonus issue|sub-division of shares)",
            "base_score": 0.75
        }
    ]

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

    def score_announcement(self, headline: str, category: str = "") -> Dict[str, Any]:
        """
        Classifies an announcement and computes an NLP materiality score (0.0 to 1.0).
        High materiality (>0.75) triggers priority alerts on the dashboard.
        """
        text = f"{category} {headline}".lower()

        matched_event = "GENERAL"
        materiality = 0.20  # Baseline routine compliance score

        for rule in self.EVENT_RULES:
            if re.search(rule["regex"], text):
                matched_event = rule["event_type"]
                materiality = rule["base_score"]
                break

        # Additional regex boost for high monetary contract values (e.g. ₹500 Cr, $100M)
        if re.search(r"(\d+[\d,]*\s*(crore|cr|million|billion))", text):
            materiality = min(1.0, materiality + 0.05)

        return {
            "event_type": matched_event,
            "materiality_score": round(materiality, 2)
        }

    def generate_announcement_id(self, symbol: str, timestamp: datetime, headline: str) -> str:
        """Generates deterministic UUID/hash for deduplication."""
        raw_key = f"{symbol}_{timestamp.isoformat()}_{headline}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()[:16]

    def parse_raw_announcements(
        self, 
        symbol: str, 
        items: List[Dict[str, Any]]
    ) -> pd.DataFrame:
        """
        Converts raw announcement items into standardized DuckDB corporate_announcements DataFrame.
        """
        records = []
        for item in items:
            headline = item.get("headline", "").strip()
            if not headline:
                continue

            category = item.get("category", "Company Update")
            ts = item.get("announcement_timestamp")
            if isinstance(ts, str):
                ts = pd.to_datetime(ts).to_pydatetime()
            elif not isinstance(ts, datetime):
                ts = datetime.now()

            score_meta = self.score_announcement(headline, category)
            ann_id = item.get("announcement_id") or self.generate_announcement_id(symbol, ts, headline)

            records.append({
                "announcement_id": ann_id,
                "symbol": symbol.upper(),
                "announcement_timestamp": ts,
                "category": category,
                "headline": headline,
                "attachment_url": item.get("attachment_url", ""),
                "materiality_score": score_meta["materiality_score"],
                "event_type": score_meta["event_type"],
                "extracted_data": item.get("extracted_data", None)
            })

        df = pd.DataFrame(records)
        if not df.empty:
            df = df.sort_values("announcement_timestamp", ascending=False).reset_index(drop=True)
        return df

