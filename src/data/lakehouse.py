"""
DuckDB Lakehouse Storage Engine for Project Titan.
Handles local columnar time-series storage, indexing, and high-performance SQL analytics.
"""

from pathlib import Path
from typing import Optional, List
import duckdb
import pandas as pd
from src.data.universe import EquityMeta


class LakehouseManager:
    """Manages the embedded DuckDB database and Parquet storage."""

    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            db_dir = Path(__file__).resolve().parent.parent.parent / "data" / "lakehouse"
            db_dir.mkdir(parents=True, exist_ok=True)
            db_path = db_dir / "equities.duckdb"
        
        self.db_path = str(db_path)
        self.conn: Optional[duckdb.DuckDBPyConnection] = None
        self.connect()
        self.init_schema()

    def connect(self) -> duckdb.DuckDBPyConnection:
        """Opens or reuses connection to DuckDB, returning a thread-safe cursor."""
        if self.conn is None:
            self.conn = duckdb.connect(database=self.db_path)
            # Enable multi-threaded query execution
            self.conn.execute("PRAGMA threads=4;")
        return self.conn.cursor()

    def close(self) -> None:
        """Closes the connection safely."""
        if self.conn is not None:
            self.conn.close()
            self.conn = None

    def init_schema(self) -> None:
        """Initializes all Phase 1 relational tables and indexes."""
        cursor = self.connect()

        # 1. Equities Registry Metadata
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS equities_meta (
                symbol VARCHAR PRIMARY KEY,
                bse_code VARCHAR UNIQUE,
                isin VARCHAR UNIQUE,
                company_name VARCHAR NOT NULL,
                sector VARCHAR NOT NULL,
                industry VARCHAR NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 2. Daily Price, Volume & Delivery Time Series
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_ohlcv (
                symbol VARCHAR NOT NULL,
                trade_date DATE NOT NULL,
                open_unadj DOUBLE NOT NULL,
                high_unadj DOUBLE NOT NULL,
                low_unadj DOUBLE NOT NULL,
                close_unadj DOUBLE NOT NULL,
                volume BIGINT NOT NULL,
                close_adj DOUBLE NOT NULL,
                delivery_qty BIGINT DEFAULT 0,
                delivery_pct DOUBLE DEFAULT 0.0,
                turnover_cr DOUBLE DEFAULT 0.0,
                PRIMARY KEY (symbol, trade_date)
            );
            CREATE INDEX IF NOT EXISTS idx_daily_symbol_date ON daily_ohlcv (symbol, trade_date);
        """)

        # 3. Corporate Actions History (Splits, Bonuses)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS corporate_actions (
                action_id VARCHAR PRIMARY KEY,
                symbol VARCHAR NOT NULL,
                ex_date DATE NOT NULL,
                action_type VARCHAR NOT NULL,
                ratio_from DOUBLE,
                ratio_to DOUBLE,
                adjustment_factor DOUBLE NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_corp_action_sym_date ON corporate_actions (symbol, ex_date);
        """)

        # 4. Point-in-Time Quarterly Fundamentals (Zero Lookahead Guard)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pit_fundamentals (
                symbol VARCHAR NOT NULL,
                period_end_date DATE NOT NULL,
                filing_timestamp TIMESTAMP NOT NULL,
                revenue_cr DOUBLE DEFAULT 0.0,
                ebitda_cr DOUBLE DEFAULT 0.0,
                ebitda_margin_pct DOUBLE DEFAULT 0.0,
                pat_cr DOUBLE DEFAULT 0.0,
                eps DOUBLE DEFAULT 0.0,
                debt_to_equity DOUBLE DEFAULT 0.0,
                promoter_holding_pct DOUBLE DEFAULT 0.0,
                pledged_promoter_pct DOUBLE DEFAULT 0.0,
                is_restated BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (symbol, period_end_date, filing_timestamp)
            );
            CREATE INDEX IF NOT EXISTS idx_pit_sym_filing ON pit_fundamentals (symbol, filing_timestamp);
        """)

        # 5. BSE Corporate Disclosures & NLP Extractions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS corporate_announcements (
                announcement_id VARCHAR PRIMARY KEY,
                symbol VARCHAR NOT NULL,
                announcement_timestamp TIMESTAMP NOT NULL,
                category VARCHAR NOT NULL,
                headline TEXT NOT NULL,
                attachment_url VARCHAR,
                materiality_score DOUBLE DEFAULT 0.0,
                event_type VARCHAR DEFAULT 'GENERAL',
                extracted_data JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_ann_sym_time ON corporate_announcements (symbol, announcement_timestamp);
            CREATE INDEX IF NOT EXISTS idx_ann_materiality ON corporate_announcements (materiality_score);
        """)

    def seed_universe(self, equities: List[EquityMeta]) -> int:
        """Seeds or updates the 50-stock metadata catalog."""
        records = [
            (eq.symbol, eq.bse_code, eq.isin, eq.company_name, eq.sector, eq.industry, eq.is_active)
            for eq in equities
        ]
        cursor = self.connect()
        cursor.executemany("""
            INSERT INTO equities_meta (symbol, bse_code, isin, company_name, sector, industry, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (symbol) DO UPDATE SET
                bse_code = excluded.bse_code,
                isin = excluded.isin,
                company_name = excluded.company_name,
                sector = excluded.sector,
                industry = excluded.industry,
                is_active = excluded.is_active;
        """, records)
        return len(records)

    def insert_daily_bars(self, df: pd.DataFrame) -> int:
        """
        Inserts or replaces daily OHLCV records.
        DataFrame must contain: symbol, trade_date, open_unadj, high_unadj,
        low_unadj, close_unadj, volume, close_adj, delivery_qty, delivery_pct, turnover_cr.
        """
        if df.empty:
            return 0
        
        cursor = self.connect()
        # Register dataframe view for ultra-fast bulk insertion
        cursor.register("df_bars_temp", df)
        cursor.execute("""
            INSERT OR REPLACE INTO daily_ohlcv 
            SELECT symbol, trade_date, open_unadj, high_unadj, low_unadj, close_unadj, 
                   volume, close_adj, delivery_qty, delivery_pct, turnover_cr 
            FROM df_bars_temp;
        """)
        cursor.unregister("df_bars_temp")
        return len(df)

    def insert_corporate_actions(self, df: pd.DataFrame) -> int:
        """Inserts or replaces corporate actions."""
        if df.empty:
            return 0
        
        cursor = self.connect()
        cursor.register("df_corp_temp", df)
        cursor.execute("""
            INSERT OR REPLACE INTO corporate_actions
            SELECT action_id, symbol, ex_date, action_type, ratio_from, ratio_to, adjustment_factor, notes, CURRENT_TIMESTAMP
            FROM df_corp_temp;
        """)
        cursor.unregister("df_corp_temp")
        return len(df)

    def get_daily_series(
        self, 
        symbol: str, 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """Retrieves daily time series for a specific symbol."""
        query = "SELECT * FROM daily_ohlcv WHERE symbol = ?"
        params = [symbol.upper()]

        if start_date:
            query += " AND trade_date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND trade_date <= ?"
            params.append(end_date)
        
        query += " ORDER BY trade_date ASC;"
        return self.connect().execute(query, params).df()

    def insert_fundamentals(self, df: pd.DataFrame) -> int:
        """Inserts or replaces Point-in-Time quarterly fundamental records."""
        if df.empty:
            return 0
        
        cursor = self.connect()
        cursor.register("df_fund_temp", df)
        cursor.execute("""
            INSERT OR REPLACE INTO pit_fundamentals
            SELECT symbol, period_end_date, filing_timestamp, revenue_cr, ebitda_cr,
                   ebitda_margin_pct, pat_cr, eps, debt_to_equity, promoter_holding_pct,
                   pledged_promoter_pct, is_restated, CURRENT_TIMESTAMP
            FROM df_fund_temp;
        """)
        cursor.unregister("df_fund_temp")
        return len(df)

    def insert_announcements(self, df: pd.DataFrame) -> int:
        """Inserts or replaces BSE corporate announcements and NLP extracts."""
        if df.empty:
            return 0
        
        cursor = self.connect()
        cursor.register("df_ann_temp", df)
        cursor.execute("""
            INSERT OR REPLACE INTO corporate_announcements
            SELECT announcement_id, symbol, announcement_timestamp, category,
                   headline, attachment_url, materiality_score, event_type,
                   extracted_data, CURRENT_TIMESTAMP
            FROM df_ann_temp;
        """)
        cursor.unregister("df_ann_temp")
        return len(df)

    def get_pit_fundamentals(
        self, 
        symbol: str, 
        as_of_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Retrieves Point-in-Time financial metrics for a symbol.
        CRITICAL: If as_of_date is provided, only statements officially filed on or before
        as_of_date are returned (guarantees ZERO lookahead bias in backtests).
        """
        query = "SELECT * FROM pit_fundamentals WHERE symbol = ?"
        params = [symbol.upper()]

        if as_of_date:
            query += " AND CAST(filing_timestamp AS DATE) <= ?"
            params.append(as_of_date)

        query += " ORDER BY filing_timestamp ASC;"
        return self.connect().execute(query, params).df()

    def get_recent_announcements(
        self, 
        symbol: Optional[str] = None, 
        min_materiality: float = 0.0,
        limit: int = 50
    ) -> pd.DataFrame:
        """Retrieves corporate announcements filtered by materiality score and symbol."""
        query = "SELECT * FROM corporate_announcements WHERE materiality_score >= ?"
        params = [min_materiality]

        if symbol:
            query += " AND symbol = ?"
            params.append(symbol.upper())

        query += " ORDER BY announcement_timestamp DESC LIMIT ?;"
        params.append(limit)
        return self.connect().execute(query, params).df()

    def get_market_summary(self) -> pd.DataFrame:
        """
        Calculates latest closing price, 20-day return, and institutional delivery score
        across all 50 stocks in one SQL query.
        """
        query = """
            WITH latest_dates AS (
                SELECT symbol, MAX(trade_date) as max_date
                FROM daily_ohlcv
                GROUP BY symbol
            ),
            ranked_bars AS (
                SELECT 
                    d.symbol,
                    d.trade_date,
                    d.close_adj,
                    d.close_unadj,
                    d.delivery_pct,
                    ROW_NUMBER() OVER (PARTITION BY d.symbol ORDER BY d.trade_date DESC) as rank
                FROM daily_ohlcv d
            )
            SELECT 
                m.symbol,
                m.company_name,
                m.sector,
                curr.close_unadj AS current_price,
                curr.close_adj AS current_price_adj,
                ROUND((curr.close_adj - past20.close_adj) / past20.close_adj * 100, 2) AS return_20d_pct,
                ROUND(curr.delivery_pct, 2) AS latest_delivery_pct
            FROM equities_meta m
            JOIN ranked_bars curr ON m.symbol = curr.symbol AND curr.rank = 1
            LEFT JOIN ranked_bars past20 ON m.symbol = past20.symbol AND past20.rank = 20
            ORDER BY m.sector, m.symbol;
        """
        return self.connect().execute(query).df()
