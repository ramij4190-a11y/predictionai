# 🚀 PredictionAI — Institutional Capital Markets & Sports AI Intelligence

**PredictionAI** is a high-performance quantitative intelligence and forecasting platform built on FastAPI, DuckDB, LightGBM, and TradingView Lightweight Charts. It provides dual-domain AI engines:

1. **Capital Markets AI Intelligence**: Institutional forecasting for NSE/BSE 50 Equities with 60–90 day quantile corridors, Macro HMM Regimes, FastDTW pattern analogies, and supply chain ontology graphs.
2. **Cricket AI Intelligence**: Bayesian Elo match forecasting, real-time in-play score tracking, 3-way win probability gauges, and self-learning post-match calibration.

---

## 🌟 Key Architecture & Capabilities

### 1. Capital Markets Intelligence
- **High-Speed DuckDB Lakehouse**: In-memory columnar analytics across 50 equities with sub-10ms response times.
- **60–90 Day Quantile Corridor Projections**: LightGBM Quantile Regressors generating 5th percentile floor, median baseline, and 95th percentile ceiling trajectories.
- **Historical Analogy Retrieval (FastDTW)**: Multidimensional Dynamic Time Warping matching current price structures to historical episodes.
- **Macro Economic Regime Detection**: Hidden Markov Model (HMM) classifying macro liquidity, inflation, and rate environments.
- **Knowledge Graph Ontology**: Cytoscape.js interactive graph visualizing customers, suppliers, and systemic risk propagation.
- **Company Filings & Financial Health**: Quarterly revenue, EBITDA margins, PAT growth, and promoter pledged share analysis.

### 2. International Cricket AI Intelligence
- **Real-Time Match Scorecard Telemetry**: Autonomous crawler fetching live runs, overs, wickets, and session states.
- **Bayesian In-Play Matrix**: 3-way win probability meter (Team A, Draw, Team B) calibrated dynamically to real-time session collapse and toss decisions.
- **Score Corridor Prediction**: Statistical 1st innings total floor, median, and ceiling corridors.
- **Self-Learning Track Record**: Evaluates model accuracy using Brier Error and logs verified "Target Hit" outcomes.

---

## 🛠️ Project Structure

```
PredictionAI/
├── data/
│   ├── config/              # Stock universe definitions (50 NSE Equities)
│   ├── lakehouse/           # DuckDB analytical databases (equities, cricket)
│   └── models/              # Pre-trained LightGBM classifiers & quantile models
├── docs/                    # Architectural phase documentation
├── scripts/                 # Lakehouse seeding, training, and sync scripts
├── src/
│   ├── backend/             # FastAPI application and REST endpoints
│   │   ├── main.py
│   │   └── static/          # Groww-style responsive UI (HTML, CSS, JS)
│   ├── cricket/             # Cricket Elo engine, lakehouse & real-time crawler
│   │   ├── cricket_brain.py
│   │   ├── cricket_lakehouse.py
│   │   └── live_crawler.py
│   ├── forecasting/         # Quantile regressors and forward corridors
│   ├── fundamentals/        # Corporate filings & financial health telemetry
│   ├── graph/               # Cytoscape supply chain ontology builder
│   ├── macro/               # Macroeconomic regime classification
│   ├── models/              # Feature engineering & directional classifiers
│   ├── rag/                 # FastDTW pattern memory
│   └── streaming/           # Tick engine and simulation stream
├── tests/                   # Test suites
├── requirements.txt         # Python dependencies
└── run_platform.bat         # Single-click launch script
```

---

## ⚡ Quick Start Guide

### 1. Prerequisites
- Python 3.10+
- Git

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/ramij4190-a11y/predictionai.git
cd predictionai

# Install dependencies
pip install -r requirements.txt
```

### 3. Launching the Platform
Run the launcher batch script:
```bash
run_platform.bat
```
Or start Uvicorn directly:
```bash
python -m uvicorn src.backend.main:app --host 127.0.0.1 --port 8000 --reload
```

Open your browser at:
- **Capital Markets AI**: [http://127.0.0.1:8000/app](http://127.0.0.1:8000/app)
- **Cricket AI Intelligence**: [http://127.0.0.1:8000/app?segment=cricket](http://127.0.0.1:8000/app?segment=cricket)
- **Interactive API Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 📜 License
MIT License. Built for high-frequency quantitative research and analytics.
