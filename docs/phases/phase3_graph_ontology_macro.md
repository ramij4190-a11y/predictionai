# Phase 3: Graph Ontology & Macro Regime Discovery
## Technical Specification & Implementation Guide

---

## 1. Phase Objective
Construct the relational knowledge graph connecting the 50 Indian equities to their supply-chain partners, raw material cost drivers, and sector competitors. Model macroeconomic market regimes (interest rates, commodity trends, liquidity cycles) and implement the macro-conditioned historical pattern analogy engine.

---

## 2. Graph Ontology Architecture (Kùzu / NetworkX)

Financial equities do not move in isolation. When crude oil or domestic steel prices surge, input costs ripple through upstream suppliers into downstream auto and consumer manufacturers with measurable margin lags.

### 2.1 Node Definitions
* **`Company`**: The 50 tracked equities (e.g. `TATAMOTORS`, `MARUTI`, `TATASTEEL`) + direct key suppliers.
* **`Sector`**: Industry classification (e.g. `Automotive`, `Specialty Chemicals`, `PSU Banking`).
* **`CommodityMacro`**: Systemic variables (e.g. `Brent Crude`, `Domestic Steel HRC`, `USDINR`, `RBI Repo Rate`).
* **`PromoterGroup`**: Conglomerate parent entities (e.g. `Tata Sons`, `Adani Group`).

### 2.2 Edge Relationships & Schema
* `(Company)-[:SUPPLIES_TO {criticality_tier: 1, revenue_exposure_pct: 0.25}]->(Company)`
* `(CommodityMacro)-[:RAW_MATERIAL_INPUT {margin_elasticity: -0.32, pass_through_days: 60}]->(Company)`
* `(Company)-[:COMPETES_WITH {sub_segment: "Passenger Vehicles"}]->(Company)`
* `(Company)-[:OWNED_BY]->(PromoterGroup)`

```cypher
-- Kùzu Cypher Schema Definition
CREATE NODE TABLE Company(symbol STRING, name STRING, market_cap_cr DOUBLE, PRIMARY KEY (symbol));
CREATE NODE TABLE CommodityMacro(indicator_id STRING, category STRING, PRIMARY KEY (indicator_id));
CREATE REL TABLE SUPPLIES_TO(FROM Company TO Company, revenue_exposure DOUBLE);
CREATE REL TABLE RAW_MATERIAL_INPUT(FROM CommodityMacro TO Company, margin_elasticity DOUBLE, pass_through_lag_days INT64);
```

---

## 3. Macroeconomic Ingestion & Regime Discovery

### 3.1 Macro Data Synchronizer
* **Reserve Bank of India (RBI DBIE)**:
  - RBI Repo Rate, Cash Reserve Ratio (CRR), Bank Credit Growth YoY, Domestic Inflation (CPI / WPI).
* **Global Macro Indicators (via FRED & yfinance)**:
  - Brent Crude Oil Futures (`BZ=F`)
  - US 10-Year Treasury Yield (`^TNX`)
  - USD/INR Currency Exchange Rate (`USDINR=X`)
  - FII & DII Net Institutional Inflows (NSE Daily Activity Reports)

### 3.2 Unsupervised Regime Classification (Hidden Markov Model)
Markets cycle through distinct liquidity regimes. The system trains a Gaussian Hidden Markov Model (`hmmlearn`) over rolling 6-month macro and market features:
* **Regime 0: Low-Volatility Expansion (Bull)**: Declining or stable interest rates, steady FII inflows, positive sector breadth.
* **Regime 1: High-Volatility Compression (Bear / Correction)**: Surging bond yields, rapid currency depreciation, persistent FII outflows.
* **Regime 2: Range-Bound Consolidation (Chop)**: Neutral monetary policy, balanced institutional flows, selective sector rotation.

---

## 4. Historical Pattern Analogy Engine (Macro-Conditioned FastDTW)

### 4.1 The Dual-Space Distance Metric
Standard chart pattern matching fails if macro regimes are inverted. The engine computes a composite distance score between the current 60-day window and every historical 60-day window from the past 15 years:

$$\text{CompositeDistance} = \alpha \cdot \text{FastDTW}(\mathbf{P}_{\text{norm}}) + (1 - \alpha) \cdot \text{Euclidean}(\mathbf{M}_{\text{regime}})$$

Where:
* $\mathbf{P}_{\text{norm}}$: Min-Max normalized price and volume accumulation vector over the 60-day lookback.
* $\mathbf{M}_{\text{regime}}$: Macro regime vector (RBI rate velocity, crude oil slope, USDINR trend, index 200-DMA distance).
* $\alpha = 0.60$ (Weighting price structure slightly above macro context).

### 4.2 Analogy Output Payload
For any analyzed equity, the engine returns the top 3 historical analogs:
```json
{
  "symbol": "TATAMOTORS",
  "analog_match_date": "2017-09-15",
  "similarity_score": 0.884,
  "macro_context_match": "Rate pause, crude recovery, domestic capex expansion",
  "historical_subsequent_6m_return": 0.421,
  "historical_max_drawdown_6m": -0.068
}
```

---

## 5. Required Implementation Modules

| File Path | Component Responsibility | Dependencies |
| :--- | :--- | :--- |
| `src/graph/ontology_builder.py` | Constructs the embedded Kùzu/NetworkX graph of equities, suppliers, and commodities. | `kuzu`, `networkx` |
| `src/graph/spillover_engine.py` | Runs network diffusion algorithms to calculate input cost inflation propagation. | `scipy.sparse` |
| `src/macro/rbi_sync.py` | Synchronizes RBI DBIE interest rate and liquidity indicators. | `httpx`, `pandas` |
| `src/macro/regime_classifier.py` | Fits Gaussian HMM to classify current macro regime state. | `hmmlearn`, `scikit-learn` |
| `src/analytics/pattern_analogy.py` | FastDTW multi-dimensional sequence matcher conditioned on macro vectors. | `fastdtw`, `tslearn` |

---

## 6. Verification & Test Suite
1. **Network Diffusion Test**: Verify that a 20% spike in raw commodity nodes propagates positive cost pressure to connected Tier-1 auto nodes.
2. **HMM Stability Test**: Confirm the regime classifier accurately identifies the 2020 COVID shock as Regime 1 (High-Vol Compression) and 2021 liquidity flood as Regime 0 (Expansion).
3. **DTW Alignment Speed**: Benchmark historical analogy search across 15 years of daily data; calculation must complete in under 500 milliseconds per stock.

