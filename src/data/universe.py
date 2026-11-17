"""
Universe Registry Manager for Project Titan.
Loads, validates, and manages the 50 Indian equities (NSE/BSE).
"""

from pathlib import Path
from typing import List, Optional, Dict
import json
from pydantic import BaseModel, Field


class EquityMeta(BaseModel):
    symbol: str = Field(..., description="NSE Trading Ticker Symbol (e.g. TATAMOTORS)")
    bse_code: str = Field(..., description="BSE Scrip Code (e.g. 500570)")
    isin: str = Field(..., description="International Securities Identification Number")
    company_name: str = Field(..., description="Full Registered Corporate Entity Name")
    sector: str = Field(..., description="Primary Economic Sector")
    industry: str = Field(..., description="Sub-industry Classification")
    is_active: bool = Field(default=True, description="Whether stock is active in tracking portfolio")

    @property
    def nse_ticker(self) -> str:
        """Returns standard Yahoo Finance / NSE symbol format."""
        return f"{self.symbol}.NS"


class UniverseManager:
    """Manages the 50-stock portfolio registry."""

    def __init__(self, config_path: Optional[Path] = None):
        if config_path is None:
            config_path = Path(__file__).resolve().parent.parent.parent / "data" / "config" / "universe_50.json"
        self.config_path = config_path
        self._equities: Dict[str, EquityMeta] = {}
        self.load()

    def load(self) -> None:
        """Loads and parses the 50-stock registry from JSON."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Universe configuration not found at {self.config_path}")
        
        with open(self.config_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
        
        self._equities = {item["symbol"]: EquityMeta(**item) for item in raw_data}

    def get_all(self) -> List[EquityMeta]:
        """Returns all registered equities."""
        return list(self._equities.values())

    def get_by_symbol(self, symbol: str) -> Optional[EquityMeta]:
        """Look up equity by NSE symbol."""
        return self._equities.get(symbol.upper())

    def get_by_bse_code(self, bse_code: str) -> Optional[EquityMeta]:
        """Look up equity by BSE code."""
        for eq in self._equities.values():
            if eq.bse_code == bse_code:
                return eq
        return None

    def get_symbols(self) -> List[str]:
        """Returns list of all 50 symbol tickers."""
        return list(self._equities.keys())

    def get_sectors(self) -> List[str]:
        """Returns unique list of sectors covered."""
        return sorted(list(set(eq.sector for eq in self._equities.values())))

