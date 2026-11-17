# Phase 4: Directional Forecast & Corridor Engine
## Technical Specification & Implementation Guide

---

## 1. Phase Objective
Construct the predictive machine learning engine to generate 2- to 8-month directional calls (Bullish/Up vs. Bearish/Down) with mathematically bounded probabilistic price corridors (5%, 50%, 95% quantiles) and non-negotiable structural invalidation stop-loss levels.

---

## 2. Mathematical Modeling Framework

### 2.1 Directional Classification Model
* **Forecasting Horizons**: $H \in \{60, 120, 180\}$ trading days (~3, 6, and 9 calendar months).
* **Target Label Formulation**:
  $$Y_{i, t}^H = \begin{cases} 
    1 & \text{if } \frac{P_{i, t+H} - P_{i, t}}{P_{i, t}} > R_f^H + 0.03 \quad (\text{Bullish Expansion}) \\ 
    0 & \text{if } \frac{P_{i, t+H} - P_{i, t}}{P_{i, t}} < -(R_f^H + 0.03) \quad (\text{Bearish Contraction}) \\
    \text{NULL} & \text{otherwise} \quad (\text{Neutral Chop Deadband - Dropped from Training})
  \end{cases}$$
  *(where $R_f^H$ is the prorated risk-free rate and $0.03$ is a 3% excess return deadband to eliminate indecisive range-bound noise).*
* **Primary Classifier**: Regularized `LightGBM` / `CatBoost` optimizing Binary Cross-Entropy Loss.

### 2.2 Feature Engineering Matrix
1. **Fundamental Momentum**:
   - $\Delta$ YoY EBITDA Margin
   - Sales Growth Acceleration ($\text{Growth}_{Q} - \text{Growth}_{Q-1}$)
   - Debt-to-Equity trajectory
   - Promoter pledge delta ($\Delta$ Pledged %)
2. **Volume Profile & Accumulation**:
   - 20-day vs. 60-day Institutional Delivery Ratio ($\text{DeliveryPct}_{20} / \text{DeliveryPct}_{60}$)
   - Distance from Anchored VWAP (anchored to prior 52-week breakout or earnings release)
   - Relative Strength vs. Nifty 50 Index ($\text{RS}_{60}$)
3. **Graph Spillover & Macro Context**:
   - Upstream supplier input-cost inflation index (from Phase 3 graph)
   - Current Macro Regime ID (from Phase 3 HMM)
   - Yield curve slope (US 10Y - 2Y) and Brent crude 30-day velocity

### 2.3 Probabilistic Corridors via Conformal Quantile Regression
Rather than outputting a single speculative price target, the platform calculates uncertainty bands:
* Trains LightGBM Quantile Regressors for quantiles $\alpha \in \{0.05, 0.25, 0.50, 0.75, 0.95\}$ across forward horizons $t + \tau$ where $20 \le \tau \le 180$.
* Pinball Loss formulation:
  $$\mathcal{L}_{\alpha}(y, \hat{y}) = \max(\alpha(y - \hat{y}), (1 - \alpha)(\hat{y} - y))$$
* Applies **Split Conformal Prediction** (`mapie`) over out-of-fold calibration data to guarantee non-parametric coverage bounds:
  $$\mathbb{P}\left(P_{t+\tau} \in [\hat{C}_{0.05}(t+\tau), \hat{C}_{0.95}(t+\tau)]\right) \ge 0.90$$

---

## 3. Structural Invalidation Protocol (Stop-Loss Math)

Every bullish or bearish directional call MUST have an exact, non-negotiable structural invalidation level:

1. **Price Structure Invalidation (Technical)**:
   - For Bullish calls: The lowest high-volume node of the preceding 3-month accumulation base, or a weekly close below the Anchored VWAP.
   - For Bearish calls: A weekly close above the highest volume distribution shelf of the preceding breakdown.
2. **Fundamental Thesis Invalidation**:
   - Quarterly results report an EBITDA margin contraction exceeding 250 bps ($>2.5\%$).
   - Promoter share pledging increases by more than 2% in a single quarter.
3. **UI Invalidation Trigger**:
   - If current market price breaches the invalidation floor, the dashboard immediately changes the status badge to **INVALIDATED (EXIT / RE-EVALUATE)** in pulsing crimson, neutralizing the thesis.

---

## 4. Cross-Validation & Validation Engine

### Purged & Embargoed Walk-Forward Validation
Standard $k$-fold cross-validation is mathematically invalid in time series. The model uses the López de Prado methodology:
* **Purging**: Training samples whose forward 2- to 8-month return window overlaps with the test set evaluation window are completely removed.
* **Embargoing**: A 30-day buffer period is added immediately after the test set to eliminate auto-regressive memory leakage into the subsequent training split.

```
[--- Train Split ---] [Purge] [--- Test Split (6 Months) ---] [Embargo] [--- Next Train ---]
```

---

## 5. Required Implementation Modules

| File Path | Component Responsibility | Dependencies |
| :--- | :--- | :--- |
| `src/models/feature_pipeline.py` | Assembles technical, fundamental, graph, and macro features with PIT guardrails. | `duckdb`, `pandas` |
| `src/models/directional_classifier.py` | LightGBM binary classifier training and walk-forward validation. | `lightgbm`, `scikit-learn` |
| `src/models/quantile_corridors.py` | Quantile LightGBM models + MAPIE split conformal prediction calibration. | `lightgbm`, `mapie` |
| `src/models/invalidation_engine.py` | Computes anchored VWAP and volume profile structural stop-loss levels. | `scipy`, `numpy` |
| `src/models/model_registry.py` | Serializes trained models into `.joblib` / `.onnx` for real-time serving. | `joblib`, `onnxruntime` |

---

## 6. Verification & Test Suite
1. **Purged Walk-Forward Audit**: Verify zero overlapping samples between training splits and test evaluation horizons.
2. **Conformal Coverage Test**: Assert that at least 88% of out-of-sample forward prices fall inside the 90% conformal corridor $[\hat{C}_{0.05}, \hat{C}_{0.95}]$.
3. **Invalidation Response Test**: Simulate an artificial 10% flash drop past the stop-loss level; assert that model state switches to `INVALIDATED` within 10 milliseconds.

