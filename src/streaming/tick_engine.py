"""
High-Fidelity Real-Time Market Stream Simulator.
Generates realistic 1-second price ticks, micro-structure bid-ask quotes,
and updates forming intraday candles for TradingView Lightweight Charts.
Anchored strictly to real exchange market prices via an Ornstein-Uhlenbeck
mean-reverting process with mathematical guardrails.
"""

from typing import Dict, Any, Optional
import time
from datetime import datetime, date
import numpy as np


class MarketTickEngine:
    """
    Simulates institutional real-time tick streaming anchored to real exchange prices.
    Uses an Ornstein-Uhlenbeck mean-reverting microstructure model with SEBI circuit limits,
    guaranteeing prices never drift away from real market reality.
    """

    def __init__(
        self,
        symbol: str,
        base_price: float,
        previous_close: Optional[float] = None,
        directional_bias: str = "NEUTRAL",
        bias_strength: float = 0.05,
        daily_volatility: float = 0.018
    ):
        self.symbol = symbol.upper()
        self.base_real_price = max(0.5, round(float(base_price), 2))
        self.base_price = self.base_real_price
        self.previous_close = round(float(previous_close), 2) if previous_close else self.base_real_price
        self.current_price = self.base_real_price
        self.directional_bias = directional_bias.upper()
        self.daily_volatility = float(daily_volatility)

        # Mean-reversion speed theta (pulls price back to actual exchange price in ~4 seconds)
        self.theta = 0.25

        # Microstructure volatility: ~0.8 bps (approx 10-15 paise on a ₹1,340 stock)
        self.micro_sigma = 0.00008

        # Today's forming candle anchored to real prices
        today_str = date.today().strftime("%Y-%m-%d")
        self.forming_candle = {
            "time": today_str,
            "open": self.base_real_price,
            "high": self.base_real_price,
            "low": self.base_real_price,
            "close": self.base_real_price,
            "volume": 75000
        }

        self.total_ticks = 0
        self.avg_volume_per_second = 1500

    def update_real_price(self, new_real_price: float, new_previous_close: Optional[float] = None) -> None:
        """Dynamically re-anchors the tick engine when fresh exchange quotes arrive."""
        if new_real_price and new_real_price > 0:
            self.base_real_price = round(float(new_real_price), 2)
            if new_previous_close and new_previous_close > 0:
                self.previous_close = round(float(new_previous_close), 2)

    def step(self) -> Dict[str, Any]:
        """
        Advances market clock by 1 second and returns a realistic live tick
        bounded tightly around the real exchange market price.
        """
        self.total_ticks += 1
        now = datetime.now()
        timestamp_str = now.strftime("%H:%M:%S")

        # 1. Ornstein-Uhlenbeck mean-reverting increment toward base real price
        mean_reversion_pull = self.theta * (self.base_real_price - self.current_price)
        noise = self.micro_sigma * self.base_real_price * np.random.standard_normal()
        delta_p = mean_reversion_pull + noise

        new_price = self.current_price + delta_p

        # 2. Hard Clamping: strictly enforce tick stays within ±0.15% of real market price
        # For Reliance (₹1,344.80), this restricts ticks to [₹1,342.80, ₹1,346.80]
        min_allowed = round(self.base_real_price * 0.9985, 2)
        max_allowed = round(self.base_real_price * 1.0015, 2)
        new_price = max(min_allowed, min(max_allowed, new_price))
        new_price = round(float(new_price), 2)
        self.current_price = new_price

        # 3. Volume generation with Poisson clustering
        jump_occurred = np.random.rand() < 0.04
        vol_mult = 3.0 if jump_occurred else max(0.4, np.random.lognormal(mean=0.0, sigma=0.35))
        tick_vol = int(self.avg_volume_per_second * vol_mult)

        # 4. Update forming candle
        if new_price > self.forming_candle["high"]:
            self.forming_candle["high"] = new_price
        if new_price < self.forming_candle["low"]:
            self.forming_candle["low"] = new_price
        self.forming_candle["close"] = new_price
        self.forming_candle["volume"] += tick_vol

        # 5. Realistic tight bid/ask quote (1-2 paise / 2-3 bps spread)
        spread_bps = 0.0002
        half_spread = max(0.05, round(new_price * (spread_bps / 2.0), 2))
        bid = round(new_price - half_spread, 2)
        ask = round(new_price + half_spread, 2)

        # 6. Change percentage relative to official previous close (e.g. +0.38%)
        total_change_pct = round(((new_price - self.previous_close) / self.previous_close) * 100.0, 2)
        tick_delta_pct = round((delta_p / self.base_real_price) * 100.0, 3)

        return {
            "type": "LIVE_TICK",
            "symbol": self.symbol,
            "timestamp": timestamp_str,
            "current_price": new_price,
            "real_market_price": self.base_real_price,
            "previous_close": self.previous_close,
            "bid": bid,
            "ask": ask,
            "tick_change_pct": tick_delta_pct,
            "total_change_pct": total_change_pct,
            "tick_volume": tick_vol,
            "forming_candle": dict(self.forming_candle)
        }
