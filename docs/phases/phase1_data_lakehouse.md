# Phase 1: Data Lakehouse & Normalization Engine
## Technical Specification & Implementation Guide

---

## 1. Phase Objective
Construct the local-first data foundation for 50 selected Indian equities (NSE/BSE). Ingest complete daily and historical Bhavcopy records from exchange listing date to present, implement split/bonus corporate action normalization, and store time series in a high-speed, local DuckDB Parquet lakehouse.

---

## 2. Directory & Storage Structure
All data runs locally under `d:\PreAI\data\`:
```
d:\PreAI\data\
├── raw\
│   └── bhavcopy\              # Compressed raw daily Bhavcopy archives (.zip / .csv)
│       └── YYYY\MM\
├── lakehouse\
│   ├── equities.duckdb        # Main DuckDB catalog and relational tables
│   └── parquet\               # Columnar partitioned time-series storage
│       ├── daily_ohlcv\       # Partitioned by symbol=XYZ/year=YYYY.parquet
│       └── corporate_actions\ # Splits, bonuses, dividends metadata
└── config\
    └── universe_50.json       # Config of the 50 tracked Indian equities
```

---

## 3. Data Ingestion Architecture

### 3.1 Data Sources (Free & Open Source)
1. **NSE Daily Bhavcopy**:
   - URL: `https://archives.nseindia.com/content/historical/EQUITIES/YYYY/MON/cmDDMONYYYYbhav.csv.zip`
   - Secondary NSE Endpoint: `https://nsearchives.nseindia.com/products/content/sec_bhavdata_full_DDMMYYYY.csv` (contains delivery percentage data).
2. **Historical Backfill**:
   - `jugaad-data`: Python library downloading historical NSE Bhavcopies and delivery statistics.
   - `yfinance` fallback: Automated fallback for missing holiday or weekend bar alignments.

### 3.2 Dual-Series Price Engine
To avoid lookahead bias and technical calculation errors, the system maintains two parallel price series:
* **Unadjusted Price (`open_unadj`, `high_unadj`, `low_unadj`, `close_unadj`)**:
  - Kept strictly as traded on the historical date.
  - Used for nominal support/resistance levels, anchored VWAP calculation, and psychological price invalidation floors.
* **Split/Bonus Adjusted Price (`close_adj`)**:
  - Back-adjusted using the cumulative split and bonus factor:
    $$\text{Factor}_t = \prod_{\tau > t} \text{SplitRatio}_\tau$$
  - Used for return calculations, statistical volatility, moving averages, and pattern matching.

---

## 4. DuckDB Storage Schema

```sql
-- Tracked Equities Registry
CREATE TABLE IF NOT EXISTS equities_meta (
    symbol VARCHAR PRIMARY KEY,       -- e.g., 'TATAMOTORS'
    bse_code VARCHAR UNIQUE,          -- e.g., '500570'
    isin VARCHAR UNIQUE,              -- e.g., 'INE155A01022'
    company_name VARCHAR NOT NULL,
    sector VARCHAR NOT NULL,
    industry VARCHAR NOT NULL,
    listing_date DATE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- Daily Market Time Series
CREATE TABLE IF NOT EXISTS daily_ohlcv (
    symbol VARCHAR NOT NULL,
    trade_date DATE NOT NULL,
    open_unadj DOUBLE NOT NULL,
    high_unadj DOUBLE NOT NULL,
    low_unadj DOUBLE NOT NULL,
    close_unadj DOUBLE NOT NULL,
    volume BIGINT NOT NULL,
    close_adj DOUBLE NOT NULL,
    delivery_qty BIGINT,
    delivery_pct DOUBLE,               -- Percentage of volume delivered (institutional proxy)
    turnover_cr DOUBLE,                -- Total turnover in INR Crores
    PRIMARY KEY (symbol, trade_date)
);

-- Corporate Actions History
CREATE TABLE IF NOT EXISTS corporate_actions (
    action_id VARCHAR PRIMARY KEY,
    symbol VARCHAR NOT NULL,
    ex_date DATE NOT NULL,
    action_type VARCHAR NOT NULL,      -- 'SPLIT', 'BONUS', 'RIGHTS', 'DIVIDEND'
    ratio_from DOUBLE,
    ratio_to DOUBLE,
    adjustment_factor DOUBLE NOT NULL,
    notes TEXT
);
```

---

## 5. Required Implementation Modules

| File Path | Component Responsibility | Dependencies |
| :--- | :--- | :--- |
| `src/data/universe.py` | Loads and manages the 50-stock universe configuration. | `pydantic` |
| `src/data/bhavcopy_fetcher.py` | Automated downloader for daily NSE Bhavcopies and delivery reports. | `httpx`, `jugaad-data` |
| `src/data/corporate_actions.py` | Computes cumulative adjustment factors for stock splits and bonuses. | `duckdb`, `pandas` |
| `src/data/lakehouse.py` | DuckDB database connection manager, Parquet partitioning, and SQL query layer. | `duckdb`, `pyarrow` |
| `src/data/pipeline.py` | Master CLI pipeline coordinating backfill, daily sync, and database compaction. | `click`, `rich` |

---

## 6. Verification & Test Suite
Before Phase 1 is marked complete, the following tests must pass:
1. **Corporate Action Test**: Verify that a known 2:1 stock split (e.g. Tata Motors or Reliance historically) results in a smooth `close_adj` series with no 50% cliff drop.
2. **Point-in-Time Continuity Test**: Verify zero missing trading days for all 50 stocks over the last 10 years (excluding official NSE market holidays).
3. **Query Latency Test**: Benchmark a full 10-year query of OHLCV + delivery percentage across all 50 stocks in DuckDB; total execution time must remain under 100 milliseconds.

