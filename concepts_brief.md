# Indian Equities Directional Intelligence & Forecasting Platform

* **Author:** Project Lead / [Company Name Pending]
* **Date:** 2026-11-13
* **Target Universe:** 50 Custom-Selected Indian Equities (NSE/BSE)
* **Investment Horizon:** 2 to 8 Months (Positional / Swing Alpha)
* **Operator Model:** Solo Retail Investor (Personal Decision-Support Cockpit)
* **Data Stack:** 100% Free & Open-Source (Local-First Lakehouse)

---

## Overview

A high-density financial intelligence and directional forecasting platform built for a solo retail investor tracking up to 50 custom-selected Indian equities (NSE/BSE, such as Tata Motors, Reliance Industries, or Infosys). The platform continuously aggregates free, open-source data (electronic historical Bhavcopy records from listing date to present, quarterly fundamental filings, BSE corporate announcements, and macroeconomic indicators) into a local-first lakehouse. 

Using an embedded graph ontology (representing company supply chains, sector competitors, and raw material inputs) combined with regularized gradient boosting and conformal quantile regression, the system projects 2- to 8-month directional trajectories (Bullish/Up vs. Bearish/Down) with probabilistic price corridors, historical pattern analogies, and structural invalidation levels. The visual interface delivers a dark-mode, Palantir-inspired command center featuring split-pane graph topology and interactive quantile corridors.

---

## Analysis & Architectural Decisions

### 1. Operational Horizon Realism: The 2-to-8-Month Positional Sweet Spot
* **Alpha Mechanics**: Ultra-short intraday time horizons are dominated by institutional co-location latency, algorithmic high-frequency trading (HFT), and dealer options gamma flows. Multi-year horizons are dominated by broad market beta. The 2-to-8-month horizon (1 to 3 earnings quarters) is the optimal window for retail alpha, capturing:
  - Quarterly earnings surprises and operating margin expansion.
  - Domestic institutional sector rotations (e.g., Capital Goods, Defense, IT, Specialty Chemicals).
  - Multi-month base accumulation breakouts that outlast daily noise.

### 2. Inventive Contradictions & TRIZ Architectural Resolutions
* **Contradiction 1: High Information Density vs. Solo Operator Cognitive Exhaustion**
  * *TRIZ Principle 10 (Preliminary Action / Inversion) — "Invalidation-First" Alerting*: A solo investor cannot inspect 50 complex graphs and models daily. The platform defaults to a "Quiet Monitoring Mode" and only elevates priority alerts when:
    1. Current price approaches within 2.5% of its structural invalidation level (stop-loss threshold).
    2. A newly filed BSE announcement breaches an NLP materiality threshold (e.g., promoter pledge changes, major contract awards, auditor resignations).
    3. Price diverges significantly from its matched historical analogy corridor.
* **Contradiction 2: Free Scraped Data Fragility vs. Mission-Critical Reliability**
  * *TRIZ Principle 24 (Intermediary) & Principle 11 (Beforehand Cushioning) — Self-Healing Fallback Fabric*: NSE and BSE frequently change scraping endpoints and bot-detection rules. The pipeline decouples raw downloads from model features. If daily live scraping encounters blocks, the system falls back to secondary open endpoints (e.g., Yahoo Finance daily bars), marks the data freshness badge on the UI, and widens the probabilistic forecast corridor to reflect data latency.
* **Contradiction 3: Regime Shifts vs. Blind Historical Analogy Matching**
  * *TRIZ Principle 35 (Parameter Changes) & Principle 15 (Dynamism) — Macro-Conditioned Dual-Space Matching*: Chart patterns cannot be matched in isolation. A consolidation in 2024 does not match a consolidation in 2007 if interest rate cycles and crude oil trends are inverted. The analogy engine computes a combined distance metric:
    $$\text{Distance} = \alpha \cdot \text{FastDTW}(\text{NormalizedPriceShape}) + (1 - \alpha) \cdot \text{Euclidean}(\text{MacroRegimeVector})$$

### 3. Local-First Engineering & Point-in-Time (PIT) Data Integrity
* **Prevention of Lookahead Bias**: Backtesting fundamental momentum requires strict prevention of lookahead bias. Standard data providers erroneously map Q3 results back to December 31st, even though Indian companies report results between January 15 and February 14. The DuckDB storage engine enforces a `filing_timestamp` column; models only access financial figures on `filing_timestamp + 1 trading day`.
* **Dual-Series Price Normalization**:
  - *Split-Adjusted Series*: Used for return calculations, volatility cones, and pattern matching.
  - *Unadjusted Series*: Used for nominal support/resistance levels, anchored VWAP calculation, and psychological stop-loss floors.
* **Storage Footprint**: For 50 stocks, 15 years of daily Bhavcopy data requires less than 15 MB in DuckDB Parquet storage. The complete graph ontology (50 equities + 100 suppliers + 15 macro variables) requires approximately 200 nodes and 600 edges, executing at 60 FPS in client-side WebGL/Canvas.

```sql
-- Core Lakehouse Schema (DuckDB)
CREATE TABLE daily_ohlcv (
    symbol VARCHAR,
    trade_date DATE,
    open_unadj DOUBLE,
    high_unadj DOUBLE,
    low_unadj DOUBLE,
    close_unadj DOUBLE,
    volume BIGINT,
    close_adj DOUBLE,
    delivery_pct DOUBLE,
    PRIMARY KEY (symbol, trade_date)
);

CREATE TABLE pit_fundamentals (
    symbol VARCHAR,
    period_end_date DATE,
    filing_timestamp TIMESTAMP,
    net_sales DOUBLE,
    ebitda DOUBLE,
    pat DOUBLE,
    eps DOUBLE,
    promoter_holding_pct DOUBLE,
    pledged_promoter_pct DOUBLE,
    PRIMARY KEY (symbol, period_end_date)
);
```

### 4. Mathematical Forecasting & Corridor Construction
* **Directional Target Classification**: Evaluates binary return $Y_{i, t}^H \in \{0, 1\}$ over forward horizons $H \in \{60, 120, 180\}$ trading days with a 3% neutrality deadband:
  $$Y_{i, t}^H = \begin{cases} 1 & \text{if } \frac{P_{i, t+H} - P_{i, t}}{P_{i, t}} > R_f^H + 0.03 \\ 0 & \text{if } \frac{P_{i, t+H} - P_{i, t}}{P_{i, t}} < -(R_f^H + 0.03) \end{cases}$$
* **Probabilistic Conformal Quantile Ribbons**: Avoids assuming Gaussian normality. Trains LightGBM quantile regressors for $\alpha \in \{0.05, 0.25, 0.50, 0.75, 0.95\}$ with split conformal calibration, rendering a shaded expansion fan on the dashboard.
* **Structural Invalidation Rules**: Bullish forecasts are invalidated if weekly closing price breaches the anchored VWAP of the preceding accumulation base or if quarterly results report an EBITDA margin contraction exceeding 250 bps.

---

## Machine Learning Toolchain & Training Architecture

| ML / AI Component | Specific Libraries | Training Target & Loss Function | Technical Rationale |
| :--- | :--- | :--- | :--- |
| **Directional Trend Classifier** | **`lightgbm`**, **`catboost`** | **Binary Cross-Entropy Loss** with L1/L2 regularization to classify forward return $Y_{t+H} \in \{0, 1\}$ over 60, 120, and 180 trading days. | Tree-based gradient boosting consistently outperforms deep neural networks on tabular features (financial ratios, delivery volume spikes, macro indices) and trains on standard CPU hardware. |
| **Probabilistic Price Corridors** | **`lightgbm`** (Quantile Objective), **`mapie`** | **Pinball / Quantile Loss**: Trains separate models for $\alpha \in \{0.05, 0.50, 0.95\}$. Calibrated via Split Conformal Prediction (`mapie`). | Generates mathematically bounded uncertainty intervals (not single-line guesses) without assuming Gaussian normal distributions. |
| **Time-Series Validation Engine** | **`scikit-learn`**, **`mlfinlab`** | **Purged & Embargoed Walk-Forward Cross-Validation**: Eliminates lookahead bias by purging overlapping test windows and embargoing auto-regressive memory. | Standard $k$-fold cross-validation is mathematically invalid in finance because it leaks future price information into past training splits. |
| **Historical Pattern Analogy Engine** | **`fastdtw`**, **`tslearn`**, **`scipy`** | **Dynamic Time Warping (DTW)** distance minimization over normalized 60-day price/volume trajectories, conditioned by macro-vector Euclidean distance. | DTW identifies structural chart bases and accumulation patterns even if the historical base took 45 days and the current base took 65 days. |
| **Macro Regime Detection** | **`hmmlearn`** (Hidden Markov Models) | **Expectation-Maximization (EM)** to identify 3 latent market states: *Expansion (Low-Vol Bull), Compression (High-Vol Bear), Stagnation (Range-Bound)*. | Allows the directional classifier to adapt its feature weights depending on the prevailing central bank liquidity regime. |
| **Graph Spillover & Contagion Engine** | **`networkx`**, **`scipy.sparse`** | **Personalized PageRank & Network Diffusion**: Propagates input-cost inflation (e.g. crude oil or steel spikes) down supply-chain edges. | Graph algorithms quantify upstream supplier margin pressure and convert network topology into numerical features for the LightGBM models. |
| **Local Announcement NLP** | **`ollama`** (`qwen2.5:7b` / `llama3.2:3b`), **`sentence-transformers`** | **Zero-shot JSON schema extraction** on BSE announcement PDFs (promoter pledge disclosures, order wins, capacity expansion). | 100% offline and free; eliminates recurring OpenAI/Claude token costs while extracting structured key-value pairs from corporate filings. |
| **Model Serialization & Serving** | **`joblib`**, **`onnxruntime`** | Serializes trained trees and scalers into lightweight binaries for sub-millisecond inference in the FastAPI backend. | Decouples model training (offline batch/weekly process) from live dashboard querying (instant response time). |

---

## Technology Stack Specification

| Architecture Layer | Core Technology | Primary Responsibility | Technical Justification | Rejected Alternative & Reason |
| :--- | :--- | :--- | :--- | :--- |
| **Data Lakehouse & Storage** | **DuckDB** + **Parquet** | Local time-series and fundamental storage | Embedded OLAP engine requiring zero background daemon; executes sub-millisecond SQL queries over 15+ years of Bhavcopy files in under 15 MB of memory. | *PostgreSQL / TimescaleDB*: Requires running a continuous background service and high RAM overhead for a personal 50-stock setup. |
| **Graph Ontology Engine** | **Kùzu** / **NetworkX** | Relational graph modeling for supply chains and sectors | Embedded in-process graph engine with native Cypher query support, interfacing directly with DuckDB and Python. | *Neo4j Server*: Rejected due to Java Virtual Machine (JVM) memory bloat and port management overhead. |
| **Data Ingestion & Parsing** | **Python 3.11+**, `jugaad-data`, `pypdf`, `yfinance` | Daily Bhavcopy downloads, BSE announcement parsing, macro data sync | Handles Indian market file formats natively (`.zip` Bhavcopies, XBRL, PDF disclosures) with built-in fallbacks. | *Commercial Data Feeds (Bloomberg/TrueData)*: Rejected due to prohibitive subscription costs (\$200–\$2,000/month). |
| **Backend Application API** | **FastAPI** + **Uvicorn** + **Pydantic v2** | REST endpoints, WebSocket telemetry, orchestration scheduler | Asynchronous execution, strict data contract validation, and real-time streaming of calculation updates. | *Django / Flask*: Rejected due to heavier framework footprint and lack of native async streaming. |
| **Frontend UI Framework** | **Next.js 15 / Vite (React 19)** + **TypeScript** | Palantir dark-mode desktop cockpit | Strict type-safety, instant Hot Module Replacement (HMR), and component modularity. | *Streamlit / Dash*: Rejected due to rigid layout boundaries and poor support for high-frequency interactive canvas rendering. |
| **Financial Time-Series Viz** | **TradingView Lightweight Charts** | Interactive candlestick & quantile ribbon rendering | Hardware-accelerated HTML5 Canvas engine designed specifically for institutional financial charting with minimal CPU usage. | *Plotly / Chart.js*: Rejected due to sluggish performance when rendering multi-thousand-bar historical overlays with live ribbons. |
| **Graph Topology Viz** | **Cytoscape.js** / **React Flow** | Interactive supply chain and sector dependency canvas | High-performance WebGL/Canvas graph layouts with support for ego-network filtering and animated flow edges. | *D3.js (from scratch)*: Rejected due to excessive boilerplate required for interactive node dragging and physics simulations. |
| **Design System & Styling** | **Tailwind CSS** + **shadcn/ui** | High-density dark telemetry theme | Atomic CSS enabling the Palantir dark slate palette (`#080C14`), crisp data density, and consistent UI state styling. | *Material UI / Ant Design*: Rejected due to opinionated enterprise light styling and runtime CSS-in-JS performance penalties. |

---

## Goals vs. Non-Goals

### In-Scope Goals
* **Automated Data Fabric**: Daily post-market (16:30 IST) Bhavcopy ingestion, BSE announcement RSS polling, and RBI DBIE macro synchronizer stored in local DuckDB Parquet tables.
* **Dynamic Graph Ontology**: Embedded Kùzu / NetworkX graph representing the 50 equities, their direct Tier-1 suppliers, domestic raw material dependencies, and sector peers.
* **Directional Forecast & Corridor Engine**: Conformal quantile regression generating 2- to 8-month bullish/bearish projections with explicit invalidation floors.
* **Historical Pattern Analogy Engine**: Macro-conditioned FastDTW matching showing side-by-side historical precedent cards.
* **Palantir-Style Mission Control Cockpit**: Local web dashboard (Next.js/Vite, Tailwind, TradingView Lightweight Charts, Cytoscape.js) with 3-pane split layout and ego-network scoping.

### Out-of-Scope Non-Goals
* **Automated Broker Order Execution**: No direct trading API connections; strictly a personal decision-support intelligence platform.
* **Microsecond Level-2/3 Tick Processing**: Discarded as irrelevant noise for a 2- to 8-month positional horizon.
* **Commercial Paid Terminals**: No reliance on Bloomberg, Refinitiv, or expensive proprietary APIs.
* **Multi-User Cloud Hosting**: Designed exclusively as a local-first single-operator system.

---

## Alternatives Weighed

* **PostgreSQL / TimescaleDB Server**: Rejected by reviewers. Requires local daemon management and high RAM overhead for a personal 50-stock setup. Replaced by embedded **DuckDB**, which queries Parquet files directly with zero operational maintenance.
* **Neo4j Enterprise Server**: Rejected due to JVM memory consumption and server overhead. Replaced by **Kùzu** (embedded C++ graph DB) or in-memory NetworkX with DuckDB relational backing.
* **Deep LSTMs / Transformers for Price Forecasting**: Rejected due to high risk of overfitting on non-stationary financial series and unnecessary GPU compute costs. Replaced by **LightGBM Quantile Regressors** and **Conformal Prediction**.
* **Unconstrained Full-Universe Scraping (Nifty 500)**: Rejected by reviewers due to rate-limiting risks, data sparsity in smallcaps, and cognitive clutter. Restricting to a curated 50-stock basket guarantees low latency and high data integrity.
* **Standard k-fold Cross-Validation**: Rejected due to auto-regressive leakage in financial time series. Replaced by **Purged & Embargoed Walk-Forward Cross-Validation**.

---

## Key Decisions & Staging for Next Steps

### Final Engineering Decisions
1. **Target Universe**: 50 custom-selected Indian equities (NSE/BSE).
2. **Horizon**: 2 to 8 months (swing/positional alpha).
3. **Storage Engine**: Embedded DuckDB with Parquet partitions.
4. **Graph Engine**: Embedded Kùzu / NetworkX with DuckDB relational backing.
5. **AI/ML Engine**: LightGBM (Directional & Quantiles), MAPIE (Conformal Calibration), FastDTW (Pattern Analogies), HMMlearn (Regimes), Ollama (Local PDF NLP).
6. **Frontend**: Vite + React 19 / Next.js 15, Tailwind CSS, TradingView Lightweight Charts, Cytoscape.js.
7. **Execution Architecture**: Invalidation-First Alerting; local-first desktop single-operator mode.

### Five-Phase Implementation Roadmap
* **Phase 1 (Days 1–7): Data Lakehouse & Normalization Engine**: Daily Bhavcopy parser, corporate action adjuster, DuckDB historical Parquet storage.
* **Phase 2 (Days 8–14): Fundamentals & BSE Announcements**: Screener.in / BSE scraper with strict `filing_timestamp` tracking and local Ollama PDF extraction.
* **Phase 3 (Days 15–21): Graph Ontology & Macro Regimes**: Kùzu/NetworkX supply-chain graph, RBI DBIE macro synchronizer, FastDTW pattern analogy engine.
* **Phase 4 (Days 22–27): Directional Forecast & Corridor Engine**: Conformal quantile LightGBM models with structural invalidation calculations and purged walk-forward validation.
* **Phase 5 (Days 28–30): Palantir Dark-Mode Cockpit**: Vite/React dashboard with TradingView charts, Cytoscape graph canvas, and single-click desktop launcher.
