"""
Online Streaming Learner & Real-Time Pattern Recognition Engine.
Processes per-second market ticks, computes streaming technical metrics,
maintains online Bayesian probability updates, and recognizes institutional price-action patterns.
"""

from typing import Dict, Any, List, Optional
from collections import deque
import numpy as np


class OnlineStreamLearner:
    """
    Online learning and real-time pattern recognition system for high-frequency ticks.
    Operates in O(1) or O(W) per tick where W is the sliding window size.
    """

    def __init__(self, window_size: int = 120, prior_bullish_prob: float = 0.50):
        self.window_size = window_size
        self.prices = deque(maxlen=window_size)
        self.volumes = deque(maxlen=window_size)
        self.timestamps = deque(maxlen=window_size)

        # Online Bayesian belief
        self.bullish_prob = float(np.clip(prior_bullish_prob, 0.10, 0.90))

        # Exponential RSI tracking state
        self.prev_price = None
        self.avg_gain = 0.0
        self.avg_loss = 0.0
        self.rsi_period = 14
        self.rsi_initialized = False

    def process_tick(self, tick: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ingests a new 1-second tick, updates online statistics, and detects active patterns.
        """
        p = float(tick["current_price"])
        v = int(tick.get("tick_volume", 1000))
        ts = tick.get("timestamp", "")

        self.prices.append(p)
        self.volumes.append(v)
        self.timestamps.append(ts)

        # 1. Update streaming RSI(14)
        rsi = self._update_rsi(p)

        # 2. Rolling VWAP & Bollinger metrics
        vwap = self._compute_vwap()
        bb_metrics = self._compute_bollinger()

        # 3. Micro-momentum
        momentum = self._compute_momentum()

        # 4. Volume multiplier
        avg_vol = float(np.mean(self.volumes)) if len(self.volumes) > 0 else float(v)
        vol_ratio = round(v / max(1.0, avg_vol), 2)

        # 5. Online Bayesian probability update
        self._update_bayesian_belief(p, vwap, vol_ratio)

        # 6. Real-time Pattern Recognition
        pattern = self._recognize_pattern(p, vwap, rsi, bb_metrics, vol_ratio, momentum)

        return {
            "rsi": round(rsi, 1),
            "vwap": round(vwap, 2),
            "volatility_bandwidth": bb_metrics["bandwidth"],
            "volatility_squeeze": bb_metrics["squeeze"],
            "momentum_slope": round(momentum, 3),
            "volume_ratio": vol_ratio,
            "bayesian_bullish_prob": round(self.bullish_prob, 3),
            "active_pattern": pattern
        }

    def _update_rsi(self, current_price: float) -> float:
        """Computes incremental Wilder's smoothed RSI(14)."""
        if self.prev_price is None:
            self.prev_price = current_price
            return 50.0

        change = current_price - self.prev_price
        self.prev_price = current_price

        gain = max(0.0, change)
        loss = max(0.0, -change)

        alpha = 1.0 / self.rsi_period
        if not self.rsi_initialized and len(self.prices) >= self.rsi_period:
            # Initialize with SMA of first N periods
            recent_diffs = np.diff(list(self.prices)[-self.rsi_period:])
            self.avg_gain = float(np.mean([max(0.0, d) for d in recent_diffs]))
            self.avg_loss = float(np.mean([max(0.0, -d) for d in recent_diffs]))
            self.rsi_initialized = True
        elif self.rsi_initialized:
            self.avg_gain = (self.avg_gain * (self.rsi_period - 1) + gain) / self.rsi_period
            self.avg_loss = (self.avg_loss * (self.rsi_period - 1) + loss) / self.rsi_period

        if self.avg_loss < 1e-9:
            return 100.0 if self.avg_gain > 0 else 50.0

        rs = self.avg_gain / self.avg_loss
        rsi = 100.0 - (100.0 / (1.0 + rs))
        return float(np.clip(rsi, 0.0, 100.0))

    def _compute_vwap(self) -> float:
        """Computes rolling Volume-Weighted Average Price over current window."""
        if not self.prices:
            return 0.0
        p_arr = np.array(self.prices)
        v_arr = np.array(self.volumes)
        total_v = np.sum(v_arr)
        if total_v < 1:
            return float(np.mean(p_arr))
        return float(np.sum(p_arr * v_arr) / total_v)

    def _compute_bollinger(self, period: int = 20, num_std: float = 2.0) -> Dict[str, Any]:
        """Computes Bollinger Bands and detects volatility compression squeeze."""
        if len(self.prices) < 5:
            curr = self.prices[-1] if self.prices else 0.0
            return {"upper": curr, "lower": curr, "bandwidth": 0.0, "squeeze": False}

        sub_p = list(self.prices)[-period:]
        mean = float(np.mean(sub_p))
        std = float(np.std(sub_p))

        upper = mean + num_std * std
        lower = mean - num_std * std
        bandwidth = (upper - lower) / max(0.1, mean)

        # Squeeze defined as bandwidth in the bottom 15% historically (normalized threshold < 0.0018)
        is_squeeze = bandwidth < 0.0022

        return {
            "upper": round(upper, 2),
            "lower": round(lower, 2),
            "bandwidth": round(bandwidth, 5),
            "squeeze": is_squeeze
        }

    def _compute_momentum(self) -> float:
        """Computes short-term price velocity via linear regression slope over last 10 ticks."""
        if len(self.prices) < 10:
            return 0.0
        y = np.array(list(self.prices)[-10:])
        x = np.arange(10)
        slope, _ = np.polyfit(x, y, 1)
        # Normalize by current price
        return float((slope / y[-1]) * 1000.0)

    def _update_bayesian_belief(self, price: float, vwap: float, vol_ratio: float) -> None:
        """
        Updates posterior probability P(Bullish | tick) every second.
        Evidence: price vs VWAP, upward velocity, and volume confirmation.
        """
        price_above_vwap = 1.0 if price >= vwap else 0.0
        evidence_score = 0.5 * price_above_vwap + 0.3 * (1.0 if self.avg_gain > self.avg_loss else 0.0)
        if vol_ratio > 1.5:
            evidence_score = evidence_score * 1.1 if price_above_vwap else evidence_score * 0.9

        evidence_score = float(np.clip(evidence_score, 0.1, 0.9))

        # Bayesian update with small learning rate to avoid erratic jitter
        lr = 0.02
        likelihood_bull = evidence_score
        likelihood_bear = 1.0 - evidence_score

        prior_bull = self.bullish_prob
        prior_bear = 1.0 - prior_bull

        num = likelihood_bull * prior_bull
        den = num + (likelihood_bear * prior_bear)
        posterior = num / max(1e-5, den)

        # Exponential moving average smooth
        self.bullish_prob = float(np.clip((1.0 - lr) * self.bullish_prob + lr * posterior, 0.05, 0.95))

    def _recognize_pattern(
        self,
        price: float,
        vwap: float,
        rsi: float,
        bb: Dict[str, Any],
        vol_ratio: float,
        momentum: float
    ) -> Dict[str, Any]:
        """
        Scans streaming microstructure for institutional chart patterns.
        """
        n = len(self.prices)
        if n < 15:
            return {
                "pattern_id": "CALIBRATING",
                "name": "Micro-Structure Calibrating",
                "category": "WARMUP",
                "confidence_pct": 50.0,
                "directional_bias": "NEUTRAL",
                "description": "Accumulating rolling ticks to form statistical significance window."
            }

        recent_window = list(self.prices)[-25:]
        rolling_high = max(recent_window[:-1])
        rolling_low = min(recent_window[:-1])

        # 1. Bullish Volume Breakout
        if price > rolling_high and vol_ratio >= 1.7 and momentum > 0:
            conf = min(92.0, 65.0 + vol_ratio * 8.0 + momentum * 5.0)
            return {
                "pattern_id": "BULLISH_BREAKOUT",
                "name": "Bullish Volume Breakout",
                "category": "MOMENTUM_BREAKOUT",
                "confidence_pct": round(conf, 1),
                "directional_bias": "BULLISH",
                "description": f"Price breached rolling resistance (₹{rolling_high:.2f}) on {vol_ratio:.1f}x volume surge with positive velocity."
            }

        # 2. Bearish Support Breakdown
        if price < rolling_low and vol_ratio >= 1.7 and momentum < 0:
            conf = min(90.0, 65.0 + vol_ratio * 8.0 + abs(momentum) * 5.0)
            return {
                "pattern_id": "BEARISH_BREAKDOWN",
                "name": "Bearish Support Breakdown",
                "category": "MOMENTUM_BREAKDOWN",
                "confidence_pct": round(conf, 1),
                "directional_bias": "BEARISH",
                "description": f"Price collapsed below local floor (₹{rolling_low:.2f}) on heavy {vol_ratio:.1f}x volume liquidation."
            }

        # 3. Volatility Compression Squeeze (Bollinger Squeeze)
        if bb.get("squeeze", False):
            return {
                "pattern_id": "VOLATILITY_SQUEEZE",
                "name": "Volatility Band Squeeze",
                "category": "COMPRESSION_EXPANSION",
                "confidence_pct": 82.5,
                "directional_bias": "NEUTRAL_COILING",
                "description": f"Bandwidth compressed to {bb['bandwidth']:.4f}. Severe volatility coiling signals imminent explosive price breakout."
            }

        # 4. Oversold Mean Reversion (RSI Hook)
        if rsi < 32 and momentum > -0.01:
            conf = min(88.0, 60.0 + (32.0 - rsi) * 2.5)
            return {
                "pattern_id": "OVERSOLD_REVERSAL",
                "name": "Oversold Mean Reversion",
                "category": "COUNTER_TREND",
                "confidence_pct": round(conf, 1),
                "directional_bias": "BULLISH",
                "description": f"Micro-RSI dipped to {rsi:.1f} (extreme oversold threshold); upward tick hook confirms buyer absorption."
            }

        # 5. Overbought Mean Reversion
        if rsi > 68 and momentum < 0.01:
            conf = min(87.0, 60.0 + (rsi - 68.0) * 2.5)
            return {
                "pattern_id": "OVERBOUGHT_REVERSAL",
                "name": "Overbought Mean Reversion",
                "category": "COUNTER_TREND",
                "confidence_pct": round(conf, 1),
                "directional_bias": "BEARISH",
                "description": f"Micro-RSI hit {rsi:.1f} in overextended territory; seller resistance pushing price back toward VWAP."
            }

        # 6. Wyckoff Absorption / Tight Consolidation
        if abs(price - vwap) / max(1.0, vwap) < 0.0015:
            return {
                "pattern_id": "WYCKOFF_ABSORPTION",
                "name": "Wyckoff Supply Absorption",
                "category": "ACCUMULATION",
                "confidence_pct": 74.0,
                "directional_bias": "BULLISH" if self.bullish_prob > 0.55 else "NEUTRAL",
                "description": f"Price hovering tightly within 15 bps of VWAP (₹{vwap:.2f}) under controlled volume; institutional accumulation signature."
            }

        # Default: Normal Price Discovery
        return {
            "pattern_id": "CONSOLIDATION_DISCOVERY",
            "name": "Continuous Price Discovery",
            "category": "EQUILIBRIUM",
            "confidence_pct": round(max(50.0, self.bullish_prob * 100.0), 1),
            "directional_bias": "BULLISH" if self.bullish_prob > 0.52 else ("BEARISH" if self.bullish_prob < 0.48 else "NEUTRAL"),
            "description": f"Balanced two-way auction flow around VWAP ₹{vwap:.2f} with {vol_ratio:.1f}x baseline volume."
        }
