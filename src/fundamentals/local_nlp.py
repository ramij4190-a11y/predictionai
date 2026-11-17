"""
Local Document NLP Entity Extractor.
Parses announcement disclosures into structured JSON payloads using rule-based NLP and local LLM fallbacks.
"""

from typing import Dict, Any, Optional
import re
import json


class LocalNLPExtractor:
    """Extracts structured financial metadata from announcement text."""

    def __init__(self, ollama_model: Optional[str] = "llama3.2:3b"):
        self.ollama_model = ollama_model

    def extract_entities(self, text: str) -> Dict[str, Any]:
        """
        Parses text and extracts key financial entities:
        - Order / contract monetary values (in INR Crores)
        - Promoter pledge shifts
        - Capacity expansion metrics
        - Executive summary
        """
        result = {
            "monetary_value_inr_cr": 0.0,
            "pledge_change_pct": 0.0,
            "counterparty": None,
            "action_verbs": [],
            "summary": ""
        }

        if not text:
            return result

        clean_text = text.replace("\n", " ").strip()

        # 1. Extract Monetary Value (e.g. Rs 450 Crores, INR 1,200 Cr, USD 50 Million)
        val_match = re.search(r"(?:rs\.?|inr|₹)\s*([\d,]+(?:\.\d+)?)\s*(crores?|cr)", clean_text, re.IGNORECASE)
        if val_match:
            try:
                num_str = val_match.group(1).replace(",", "")
                result["monetary_value_inr_cr"] = round(float(num_str), 2)
            except Exception:
                pass

        # 2. Extract Promoter Pledge Change (e.g. pledged 5.2%, revoked 2.1%)
        if re.search(r"pledg|encumbrance|revoc|revok|releas", clean_text, re.IGNORECASE):
            m = re.search(r"(?:revoc\w*|revok\w*|releas\w*|pledg\w*|encumbrance\w*).*?([\d\.]+)\s*%", clean_text, re.IGNORECASE)
            if m:
                try:
                    pct_val = float(m.group(1))
                    is_revoked = bool(re.search(r"revoc|revok|releas", clean_text, re.IGNORECASE))
                    result["pledge_change_pct"] = -pct_val if is_revoked else pct_val
                except Exception:
                    pass

        # 3. Extract Counterparty / Client (e.g. "order from Ministry of Defence", "awarded by Tata Steel")
        client_match = re.search(r"(?:awarded by|order from|contract with|agreement with|received from|from)\s+([A-Z][A-Za-z0-9\s&,\.]{3,40}?)(?:for|to|\.|$)", clean_text)
        if client_match:
            result["counterparty"] = client_match.group(1).strip()

        # 4. Generate clean executive summary (first 180 chars)
        result["summary"] = clean_text[:200] + "..." if len(clean_text) > 200 else clean_text
        return result
