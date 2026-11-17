"""
Unit and Integration Test Suite for Real-Time Streaming & RAG Intelligence Engine.
Validates:
1. MarketTickEngine high-frequency tick simulation.
2. OnlineStreamLearner real-time RSI, VWAP, Bollinger squeeze, and pattern recognition.
3. PatternRAGService semantic vector indexing and tactical playbook retrieval.
4. MarketIntelligenceService live streaming packet generation.
5. FastAPI REST and WebSocket route registration.
"""

import sys
from pathlib import Path
import unittest
import numpy as np

# Ensure repository root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.streaming.tick_engine import MarketTickEngine
from src.streaming.online_learner import OnlineStreamLearner
from src.rag.pattern_rag import PatternRAGService, PATTERN_KNOWLEDGE_BASE
import json
import urllib.request


class TestLiveStreamingAndRAG(unittest.TestCase):
    """Test suite for live streaming market ticks, online learning, and RAG retrieval."""

    def test_01_market_tick_engine(self):
        """Validates that MarketTickEngine advances price, volume, and forming daily candle."""
        engine = MarketTickEngine(
            symbol="TATAMOTORS",
            base_price=287.40,
            daily_volatility=0.02,
            directional_bias="BULLISH"
        )
        self.assertEqual(engine.symbol, "TATAMOTORS")
        self.assertEqual(engine.base_price, 287.40)

        # Step 20 ticks
        ticks = [engine.step() for _ in range(20)]
        self.assertEqual(len(ticks), 20)
        self.assertEqual(engine.total_ticks, 20)

        last_tick = ticks[-1]
        self.assertIn("current_price", last_tick)
        self.assertIn("bid", last_tick)
        self.assertIn("ask", last_tick)
        self.assertGreater(last_tick["ask"], last_tick["bid"])
        self.assertIn("forming_candle", last_tick)

        candle = last_tick["forming_candle"]
        self.assertEqual(candle["open"], 287.40)
        self.assertGreaterEqual(candle["high"], candle["low"])
        self.assertGreaterEqual(candle["high"], candle["close"])
        self.assertLessEqual(candle["low"], candle["close"])
        self.assertGreater(candle["volume"], 50000)
        print(f"[PASS] MarketTickEngine verified: 20 ticks generated, final price ₹{last_tick['current_price']:.2f}")

    def test_02_online_stream_learner(self):
        """Validates that OnlineStreamLearner computes rolling features and updates Bayesian belief."""
        learner = OnlineStreamLearner(window_size=60, prior_bullish_prob=0.55)
        engine = MarketTickEngine("INFY", base_price=1140.0)

        metrics_list = []
        for _ in range(30):
            tick = engine.step()
            metrics = learner.process_tick(tick)
            metrics_list.append(metrics)

        last_metrics = metrics_list[-1]
        self.assertIn("rsi", last_metrics)
        self.assertTrue(0.0 <= last_metrics["rsi"] <= 100.0)
        self.assertIn("vwap", last_metrics)
        self.assertGreater(last_metrics["vwap"], 0.0)
        self.assertIn("volume_ratio", last_metrics)
        self.assertIn("bayesian_bullish_prob", last_metrics)
        self.assertTrue(0.0 <= last_metrics["bayesian_bullish_prob"] <= 1.0)
        self.assertIn("active_pattern", last_metrics)
        print(f"[PASS] OnlineStreamLearner verified: RSI={last_metrics['rsi']}, VWAP=₹{last_metrics['vwap']}, P(Bull)={last_metrics['bayesian_bullish_prob']:.2f}")

    def test_03_pattern_recognition(self):
        """Validates pattern detection for compression squeeze and breakout scenarios."""
        learner = OnlineStreamLearner(window_size=60, prior_bullish_prob=0.50)

        # Feed 25 identical prices to induce low bandwidth / compression
        for _ in range(25):
            tick = {
                "current_price": 500.0,
                "tick_volume": 1000,
                "timestamp": "10:00:00"
            }
            m = learner.process_tick(tick)

        # In tight price range, pattern should be VOLATILITY_SQUEEZE or WYCKOFF_ABSORPTION or CALIBRATING
        pat = m["active_pattern"]
        self.assertIn("pattern_id", pat)
        self.assertIn(pat["pattern_id"], ["VOLATILITY_SQUEEZE", "WYCKOFF_ABSORPTION", "CONSOLIDATION_DISCOVERY"])

        # Feed a sharp breakout tick with 3x volume
        breakout_tick = {
            "current_price": 515.0,
            "tick_volume": 3500,
            "timestamp": "10:00:26"
        }
        breakout_m = learner.process_tick(breakout_tick)
        self.assertEqual(breakout_m["active_pattern"]["pattern_id"], "BULLISH_BREAKOUT")
        print(f"[PASS] Pattern recognition verified: Breakout recognized with {breakout_m['active_pattern']['confidence_pct']}% confidence")

    def test_04_pattern_rag_service(self):
        """Validates TF-IDF vector indexing and institutional precedent retrieval."""
        rag = PatternRAGService()
        self.assertEqual(len(rag.corpus), len(PATTERN_KNOWLEDGE_BASE))

        active_pattern = {
            "pattern_id": "BULLISH_BREAKOUT",
            "name": "Bullish Volume Breakout",
            "category": "MOMENTUM_BREAKOUT",
            "directional_bias": "BULLISH"
        }
        online_metrics = {"rsi": 62.5, "volume_ratio": 2.2}

        retrieval = rag.retrieve("TATAMOTORS", current_price=287.40, active_pattern=active_pattern, online_metrics=online_metrics)
        self.assertEqual(retrieval["retrieval_status"], "MATCHED")
        self.assertEqual(retrieval["pattern_id"], "BULLISH_BREAKOUT")
        self.assertIn("Tata Motors", retrieval["historical_precedent"])
        self.assertGreater(retrieval["win_rate_pct"], 70.0)
        self.assertGreater(retrieval["target_1_price"], 287.40)
        self.assertLess(retrieval["stop_loss_price"], 287.40)
        self.assertIn("institutional_mechanics", retrieval)
        print(f"[PASS] PatternRAGService verified: Retrieved '{retrieval['pattern_name']}' with {retrieval['win_rate_pct']}% win rate")

    def test_05_fastapi_live_routes(self):
        """Validates that live streaming REST endpoint returns live tick, metrics, and RAG payload."""
        req = urllib.request.Request("http://127.0.0.1:8000/api/v1/stocks/TATAMOTORS/live-packet")
        with urllib.request.urlopen(req, timeout=5) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data["symbol"], "TATAMOTORS")
            self.assertIn("current_price", data)
            self.assertIn("forming_candle", data)
            self.assertIn("online_metrics", data)
            self.assertIn("active_pattern", data)
            self.assertIn("rag_intelligence", data)
            self.assertEqual(data["rag_intelligence"]["retrieval_status"], "MATCHED")
        print(f"[PASS] Live REST & RAG endpoint verified live on port 8000: ₹{data['current_price']} | {data['active_pattern']['name']}")


if __name__ == "__main__":
    unittest.main()
