# Phase 5: Palantir Dark-Mode Cockpit & Desktop GUI
## Technical Specification & Implementation Guide

---

## 1. Phase Objective
Construct the user-facing command center. Build a local-first, hardware-accelerated dark-mode dashboard inspired by Palantir Gotham/Foundry aesthetics (`#080C14`). Feature a 3-panel split layout, interactive TradingView Lightweight Charts with quantile fan overlays, a Cytoscape.js supply chain topology canvas, and an invalidation-first notification system.

---

## 2. Cockpit Layout Architecture

```
+---------------------------------------------------------------------------------------------------------+
| [LOGO] TITAN PALANTIR COCKPIT  |  NSE/BSE ACTIVE  |  REGIME: LOW-VOL EXPANSION  |  REFRESH: 16:35 IST   |
+---------------------+---------------------------------------------------------+-------------------------+
| 50-STOCK WATCHLIST  | PRIMARY ANALYSIS CANVAS                                 | TELEMETRY & ANALOGY     |
| (Width: 320px)      | (Flex: 1)                                               | DRAWER (Width: 380px)   |
|                     |                                                         |                         |
| • TATAMOTORS        | [VIEW TABS: (1) Positional Corridor  | (2) Supply Graph] | • Active Analogy Match: |
|   [BULLISH] +18.4%  |                                                         |   Reliance Q2 2017 (88%)|
|   Floor: ₹890.00    | [TRADINGVIEW LIGHTWEIGHT CHART CANVAS]                   |   Subsequent 6M: +42.1% |
|                     | - Historical Split-Adjusted Candlesticks                |                         |
| • RELIANCE          | - Conformal Quantile Fan (5%, 50%, 95% Ribbons)         | • Fundamental Health:   |
|   [NEUTRAL] +2.1%   | - Stepped Red Line: Structural Invalidation Floor       |   EBITDA Margin: +180bps|
|   Floor: ₹1,240.00  | - Upcoming Catalyst Timeline Marker                     |   Promoter Pledge: 0.0% |
|                     |                                                         |                         |
| • INFY              | ------------------------------------------------------- | • Latest BSE Filings:   |
|   [BEARISH] -8.2%   | [CYTOSCAPE.JS SUPPLY CHAIN TOPOLOGY]                    |   [ORDER WIN] ₹450 Cr   |
|   Ceiling: ₹1,810   | - Direct Suppliers (Bharat Forge, Minda Corp)           |   Defence Mobility      |
|                     | - Raw Inputs (Steel, Crude) with flow velocity          |                         |
+---------------------+---------------------------------------------------------+-------------------------+
| TELEMETRY DOCK: [STATUS: IDLE] | DUCKDB SYNC: OK | RUNTIME LATENCY: 12ms | INVENTIVE MODE: QUIET        |
+---------------------------------------------------------------------------------------------------------+
```

---

## 3. UI/UX Palantir Design Tokens

* **Primary Background**: `#080C14` (Deep Abyssal Blue-Black)
* **Surface Background (Cards & Drawers)**: `#0F172A` / `#162032`
* **Border Color**: `#1E293B` (Subtle 1px border lines)
* **High-Contrast Text**: `#F8FAFC` (Slate-50)
* **Telemetry / Muted Text**: `#64748B` (Slate-500)
* **Accents & Telemetry Colors**:
  - `Cyan Accent` (`#00F0FF`): Supply chain particle flows, active selection rings
  - `Bullish Emerald` (`#10B981`): Probabilistic upside corridor, accumulation badges
  - `Bearish Rose` (`#F43F5E`): Probabilistic downside corridor, margin contraction badges
  - `Invalidation Red` (`#EF4444`): Structural stop-loss step line, thesis invalidation alarms
  - `Warning Amber` (`#F59E0B`): BSE announcement anomalies, promoter pledge increases

---

## 4. Frontend Component Hierarchy

### 4.1 Charting Engine (`TradingView Lightweight Charts`)
* Custom Series Plugin rendering the **Quantile Fan Ribbon**:
  - Upper Boundary ($q_{0.95}$): Semi-transparent emerald fill (`rgba(16, 185, 129, 0.12)`)
  - Median Trajectory ($q_{0.50}$): Dashed cyan line (`#00F0FF`)
  - Lower Boundary ($q_{0.05}$): Semi-transparent rose fill (`rgba(244, 63, 94, 0.12)`)
* Custom Price Line for **Structural Invalidation Floor**:
  - Stepped horizontal red line with a persistent tag: `INVALIDATION @ ₹890.00`.

### 4.2 Graph Topology Engine (`Cytoscape.js` / `@antv/g6`)
* **Ego-Network Scoping**: Clicking on `TATAMOTORS` automatically fades out unlinked nodes in the 50-stock basket, rendering only 1-hop and 2-hop connected entities (suppliers, raw commodities, competitors).
* **Animated Edge Flows**: SVG or Canvas pulsing dashes traversing edges to visualize raw material cost inflation flowing into manufacturer margin compression.

### 4.3 Invalidation-First Alerting Banner
* Stays collapsed during normal operation ("Quiet Monitoring").
* Expands automatically with an audible ping if any monitored stock breaches within 2.5% of its structural stop-loss floor or experiences an abnormal promoter pledge event.

---

## 5. Backend API & Telemetry Gateway (FastAPI)

```python
# Core FastAPI Endpoints
GET  /api/v1/universe/summary         # 50-stock matrix with directional badges and invalidation proximity
GET  /api/v1/stocks/{symbol}/history  # Dual-series OHLCV + delivery percentages
GET  /api/v1/stocks/{symbol}/corridor # Quantile predictions (t+20 to t+180 days) + invalidation floor
GET  /api/v1/stocks/{symbol}/analog   # Top 3 historical analog cards with macro regime matching
GET  /api/v1/stocks/{symbol}/ontology # Ego-network nodes and edges for Cytoscape.js
WS   /ws/v1/telemetry                 # WebSocket streaming real-time alerts and scraper sync progress
```

---

## 6. One-Click Desktop Deployment Launcher
The solo retail investor executes a single Windows batch script (`run_platform.bat`) to boot the local lakehouse, backend daemon, and GUI cockpit simultaneously:

```bat
@echo off
echo ========================================================
echo   TITAN PALANTIR PLATFORM - INDIAN EQUITIES INTELLIGENCE
echo ========================================================
start /b uvicorn src.backend.main:app --port 8000 --reload
cd frontend && npm run dev
```

---

## 7. Verification & Test Suite
1. **Render Frame Rate Benchmark**: Verify that the TradingView chart with 10 years of historical data + 3 quantile ribbon overlays maintains 60 FPS scrolling and panning.
2. **Ego-Network Switch Latency**: Measure time required to switch focus from `TATAMOTORS` to `RELIANCE` on the graph canvas; must execute in under 150 milliseconds.
3. **WebSocket Reconnection Test**: Assert that the client gracefully reconnects within 2 seconds if the local backend server restarts.

