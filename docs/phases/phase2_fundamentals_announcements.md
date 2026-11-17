# Phase 2: Fundamentals & BSE Announcement Pipeline
## Technical Specification & Implementation Guide

---

## 1. Phase Objective
Construct the fundamental and corporate event intelligence engine. Ingest historical quarterly financial statements, track promoter shareholding and pledging percentages, and parse real-time BSE corporate disclosures using local document intelligence without introducing lookahead bias.

---

## 2. Preventing Lookahead Bias (The Point-in-Time Requirement)
In a 2- to 8-month forecasting model, using the quarter-end date (e.g., Q3 ending on Dec 31st) to predict stock movements in January is mathematically invalid because the company does not release its results until mid-January or February.

* **Filing Timestamp Protocol**:
  - Every financial statement must store two separate timestamps:
    1. `period_end_date`: The accounting period (e.g. `2024-12-31`).
    2. `filing_timestamp`: The exact timestamp when the results were announced to BSE/NSE (e.g. `2025-02-06 18:45:00 IST`).
  - The model feature pipeline enforces that financial metrics for that quarter are only accessible on `trade_date > DATE(filing_timestamp)`.

---

## 3. Data Sources & Extraction Pipelines

### 3.1 Historical Quarterly Financials
* **Source**: Screener.in export endpoints / BSE XBRL corporate repository.
* **Metrics Ingested**:
  - Operating Income / Net Revenue
  - Operating Profit (EBITDA) & EBITDA Margin (%)
  - Net Profit After Tax (PAT) & EPS
  - Free Cash Flow & Operating Cash Flow
  - Total Debt & Debt-to-Equity Ratio
  - Promoter Shareholding (%) & Promoter Pledged Percentage (%)

### 3.2 BSE Corporate Announcements Pipeline
* **Source**: BSE Corporate Announcement API & RSS Feed:
  - Feed URL: `https://api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/...`
* **Filtering & Materiality Gating**:
  - Discard generic compliance filings (e.g. minor clerical certificates).
  - Prioritize material corporate events:
    - *Financial Results* (Quarterly / Annual)
    - *Promoter Pledging / Revocation* (Critical risk indicator in Indian equities)
    - *New Order Wins & Commercial Contracts* (Revenue expansion catalysts)
    - *Key Management Personnel (KMP) Resignations* (Governance risk)
    - *Auditor Qualifications or Resignations* (Immediate red flag)

### 3.3 Offline PDF Extraction with Local AI (Ollama)
* When a high-materiality announcement is flagged, download the attached official PDF.
* Extract text via `pypdf` or `pdfplumber`.
* Pass text to local `ollama` model (`qwen2.5:7b` or `llama3.2:3b`) with a constrained JSON schema:
```json
{
  "event_type": "ORDER_WIN | RESULTS | PLEDGE | RESIGNATION | CAPEX",
  "order_value_inr_cr": 450.0,
  "client_name": "Ministry of Defence",
  "completion_timeline_months": 18,
  "materiality_score": 0.85,
  "summary": "Tata Motors wins contract to supply 1,200 specialized mobility vehicles."
}
```

---

## 4. DuckDB Storage Schema

```sql
-- Quarterly Point-in-Time Financial Statements
CREATE TABLE IF NOT EXISTS pit_fundamentals (
    symbol VARCHAR NOT NULL,
    period_end_date DATE NOT NULL,
    filing_timestamp TIMESTAMP NOT NULL,
    revenue_cr DOUBLE,
    ebitda_cr DOUBLE,
    ebitda_margin_pct DOUBLE,
    pat_cr DOUBLE,
    eps DOUBLE,
    debt_to_equity DOUBLE,
    promoter_holding_pct DOUBLE,
    pledged_promoter_pct DOUBLE,       -- Percentage of promoter shares pledged
    is_restated BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (symbol, period_end_date, filing_timestamp)
);

-- BSE Announcements & NLP Extractions
CREATE TABLE IF NOT EXISTS corporate_announcements (
    announcement_id VARCHAR PRIMARY KEY,
    symbol VARCHAR NOT NULL,
    announcement_timestamp TIMESTAMP NOT NULL,
    category VARCHAR NOT NULL,
    headline TEXT NOT NULL,
    attachment_url VARCHAR,
    materiality_score DOUBLE,          -- 0.0 (Irrelevant) to 1.0 (Critical)
    event_type VARCHAR,                -- 'RESULTS', 'ORDER_WIN', 'PLEDGE', etc.
    extracted_data JSON,               -- Parsed JSON payload from Ollama
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 5. Required Implementation Modules

| File Path | Component Responsibility | Dependencies |
| :--- | :--- | :--- |
| `src/fundamentals/screener_client.py` | Extracts quarterly financial metrics and promoter pledge ratios. | `httpx`, `beautifulsoup4` |
| `src/fundamentals/bse_announcements.py` | Polls BSE announcement feeds every 15 minutes during trading hours. | `httpx`, `feedparser` |
| `src/fundamentals/pdf_extractor.py` | Downloads announcement PDFs and extracts clean text blocks. | `pypdf`, `pdfplumber` |
| `src/fundamentals/local_nlp.py` | Local Ollama client prompting small open models with JSON grammar constraints. | `ollama`, `pydantic` |
| `src/fundamentals/pit_validator.py` | Validates zero lookahead bias between filing dates and market prices. | `duckdb` |

---

## 6. Verification & Test Suite
1. **Zero Lookahead Audit**: Backtest simulation asserting that any trade executed on date $T$ only had access to quarterly statements with `DATE(filing_timestamp) < T`.
2. **Promoter Pledge Shift Detection**: Verify pipeline extracts promoter pledge percentage changes for high-leverage stocks.
3. **Local NLP Speed Benchmark**: PDF extraction and JSON schema parsing on an average 2-page announcement must complete in under 5 seconds on CPU/local GPU.

