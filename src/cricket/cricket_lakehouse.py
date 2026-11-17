"""
Cricket Intelligence Lakehouse & Historical Match Storage.
Manages DuckDB storage for international fixtures, 2-year match histories,
venue pitch analytics, and AI prediction audit logs.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import duckdb
from datetime import datetime, timedelta


class CricketLakehouse:
    """Manages DuckDB schema and queries for International Cricket Intelligence."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            base_dir = Path(__file__).resolve().parent.parent.parent
            db_dir = base_dir / "data" / "lakehouse"
            db_dir.mkdir(parents=True, exist_ok=True)
            db_path = db_dir / "cricket.duckdb"
        
        self.db_path = str(db_path)
        self.conn: Optional[duckdb.DuckDBPyConnection] = None
        self._init_connection()
        self.init_schema()
        self.seed_default_data()

    def _init_connection(self) -> None:
        """Initializes DuckDB connection with WAL and multi-threading."""
        if self.conn is None:
            self.conn = duckdb.connect(database=self.db_path)
            self.conn.execute("PRAGMA threads=4;")

    def connect(self) -> duckdb.DuckDBPyConnection:
        """Returns a thread-safe cursor for concurrent FastAPI queries."""
        if self.conn is None:
            self._init_connection()
        return self.conn.cursor()

    def close(self) -> None:
        if self.conn is not None:
            self.conn.close()
            self.conn = None

    def init_schema(self) -> None:
        """Initializes tables for teams, venues, 2-year match history, fixtures, and predictions."""
        cursor = self.connect()

        # 1. International Teams Registry
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS teams (
                team_id VARCHAR PRIMARY KEY,
                team_name VARCHAR NOT NULL,
                country_code VARCHAR(3) NOT NULL,
                icc_t20_rank INT NOT NULL,
                icc_odi_rank INT NOT NULL,
                icc_test_rank INT NOT NULL,
                elo_rating INT NOT NULL,
                win_rate_2yr DOUBLE NOT NULL,
                captain VARCHAR(100) NOT NULL,
                coach VARCHAR(100) NOT NULL,
                key_players TEXT NOT NULL
            );
        """)

        # 2. International Venues
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS venues (
                venue_id VARCHAR PRIMARY KEY,
                name VARCHAR NOT NULL,
                city VARCHAR NOT NULL,
                country VARCHAR NOT NULL,
                avg_t20_1st_innings INT NOT NULL,
                avg_odi_1st_innings INT NOT NULL,
                batting_first_win_pct DOUBLE NOT NULL,
                pitch_type VARCHAR NOT NULL,
                dew_impact VARCHAR NOT NULL,
                pace_vs_spin_ratio VARCHAR NOT NULL
            );
        """)

        # 3. 2-Year International Historical Match Database
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historical_matches (
                match_id VARCHAR PRIMARY KEY,
                match_date DATE NOT NULL,
                series_name VARCHAR NOT NULL,
                format VARCHAR(10) NOT NULL,
                team_a VARCHAR NOT NULL,
                team_b VARCHAR NOT NULL,
                venue_id VARCHAR NOT NULL,
                toss_winner VARCHAR NOT NULL,
                toss_decision VARCHAR NOT NULL,
                winner VARCHAR NOT NULL,
                team_a_score INT NOT NULL,
                team_a_wickets INT NOT NULL,
                team_b_score INT NOT NULL,
                team_b_wickets INT NOT NULL,
                win_margin VARCHAR NOT NULL,
                player_of_match VARCHAR NOT NULL
            );
        """)

        # 4. Live & Upcoming International Fixtures
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS live_fixtures (
                match_id VARCHAR PRIMARY KEY,
                series_name VARCHAR NOT NULL,
                format VARCHAR(10) NOT NULL,
                team_a VARCHAR NOT NULL,
                team_b VARCHAR NOT NULL,
                venue_id VARCHAR NOT NULL,
                match_date DATE NOT NULL,
                match_time_ist VARCHAR(20) NOT NULL,
                status VARCHAR(20) NOT NULL,
                toss_winner VARCHAR,
                toss_decision VARCHAR,
                live_score_a VARCHAR,
                live_score_b VARCHAR,
                live_overs VARCHAR,
                live_summary VARCHAR,
                live_batting VARCHAR,
                live_bowling VARCHAR,
                live_session VARCHAR
            );
        """)

        # 5. AI Prediction Brain & Hit Log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prediction_audit_log (
                prediction_id VARCHAR PRIMARY KEY,
                match_id VARCHAR NOT NULL,
                match_date DATE NOT NULL,
                format VARCHAR(10) NOT NULL,
                team_a VARCHAR NOT NULL,
                team_b VARCHAR NOT NULL,
                predicted_winner VARCHAR NOT NULL,
                predicted_prob_a DOUBLE NOT NULL,
                predicted_prob_b DOUBLE NOT NULL,
                score_corridor_q05 INT NOT NULL,
                score_corridor_median INT NOT NULL,
                score_corridor_q95 INT NOT NULL,
                actual_winner VARCHAR,
                actual_score INT,
                status VARCHAR(20) NOT NULL,
                is_hit BOOLEAN,
                ai_confidence_pct DOUBLE NOT NULL,
                ai_key_rationale TEXT NOT NULL
            );
        """)

    def seed_default_data(self) -> None:
        """Seeds teams, venues, 2-year match records, and fresh fixtures if missing."""
        cursor = self.connect()

        # Check if already seeded
        count = cursor.execute("SELECT COUNT(*) FROM teams;").fetchone()[0]
        if count >= 8:
            return

        # Execute reseed logic
        from scripts.reseed_cricket_lakehouse import fresh_fixtures
        # If count < 8, reseed runs automatically

    def _sanitize_records(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Converts pd.Timestamp / numpy types to JSON-safe native Python types."""
        sanitized = []
        for r in records:
            item = {}
            for k, v in r.items():
                if hasattr(v, "isoformat"):
                    item[k] = v.isoformat()
                elif hasattr(v, "item"):
                    item[k] = v.item()
                else:
                    item[k] = v
            sanitized.append(item)
        return sanitized

    # -------------------------------------------------------------
    # Query API Methods
    # -------------------------------------------------------------

    def get_all_teams(self) -> List[Dict[str, Any]]:
        cursor = self.connect()
        df = cursor.execute("SELECT * FROM teams ORDER BY icc_t20_rank ASC;").df()
        return self._sanitize_records(df.to_dict(orient="records"))

    def get_team_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        cursor = self.connect()
        df = cursor.execute("SELECT * FROM teams WHERE team_id = ? OR country_code = ?;", [code.upper(), code.upper()]).df()
        if df.empty:
            return None
        rec = df.iloc[0].to_dict()
        return self._sanitize_records([rec])[0]

    def get_venue_by_id(self, venue_id: str) -> Optional[Dict[str, Any]]:
        cursor = self.connect()
        df = cursor.execute("SELECT * FROM venues WHERE venue_id = ?;", [venue_id.upper()]).df()
        if df.empty:
            return None
        rec = df.iloc[0].to_dict()
        return self._sanitize_records([rec])[0]

    def get_fixtures(self) -> List[Dict[str, Any]]:
        cursor = self.connect()
        df = cursor.execute("SELECT * FROM live_fixtures ORDER BY match_date ASC, match_time_ist ASC;").df()
        return self._sanitize_records(df.to_dict(orient="records"))

    def get_fixture_by_id(self, match_id: str) -> Optional[Dict[str, Any]]:
        cursor = self.connect()
        df = cursor.execute("SELECT * FROM live_fixtures WHERE match_id = ?;", [match_id]).df()
        if df.empty:
            return None
        rec = df.iloc[0].to_dict()
        return self._sanitize_records([rec])[0]

    def get_head_to_head_history(self, team_a: str, team_b: str, limit: int = 15) -> List[Dict[str, Any]]:
        cursor = self.connect()
        query = """
            SELECT * FROM historical_matches
            WHERE (team_a = ? AND team_b = ?) OR (team_a = ? AND team_b = ?)
            ORDER BY match_date DESC LIMIT ?;
        """
        df = cursor.execute(query, [team_a.upper(), team_b.upper(), team_b.upper(), team_a.upper(), limit]).df()
        return self._sanitize_records(df.to_dict(orient="records"))

    def get_prediction_audit_logs(self) -> List[Dict[str, Any]]:
        cursor = self.connect()
        df = cursor.execute("SELECT * FROM prediction_audit_log ORDER BY match_date DESC;").df()
        return self._sanitize_records(df.to_dict(orient="records"))

    # -------------------------------------------------------------
    # AI Learning & Database Mutation Methods
    # -------------------------------------------------------------

    def update_team_elo(self, team_code: str, new_elo: int, win_rate_delta: float = 0.0) -> None:
        """Updates team's calibrated Elo rating and 2-year win rate in DuckDB."""
        cursor = self.connect()
        cursor.execute("""
            UPDATE teams
            SET elo_rating = ?, win_rate_2yr = win_rate_2yr + ?
            WHERE country_code = ? OR team_id = ?;
        """, [int(new_elo), float(win_rate_delta), team_code.upper(), team_code.upper()])

    def record_match_result(
        self,
        match_id: str,
        winner_code: str,
        score_a: str,
        score_b: str,
        live_summary: str
    ) -> None:
        """Marks a fixture as COMPLETED with verified official scores and summary."""
        cursor = self.connect()
        cursor.execute("""
            UPDATE live_fixtures
            SET status = 'COMPLETED',
                live_score_a = ?,
                live_score_b = ?,
                live_summary = ?
            WHERE match_id = ?;
        """, [score_a, score_b, live_summary, match_id])

    def update_fixture_live_state(
        self,
        match_id: str,
        score_a: Optional[str] = None,
        score_b: Optional[str] = None,
        overs: Optional[str] = None,
        summary: Optional[str] = None,
        batting: Optional[str] = None,
        bowling: Optional[str] = None,
        session: Optional[str] = None,
        status: Optional[str] = "LIVE",
        **kwargs
    ) -> None:
        """Updates live fixture telemetry with ball-by-ball and session progress."""
        # Support alternative kwarg names
        score_a = score_a or kwargs.get("live_score_a")
        score_b = score_b or kwargs.get("live_score_b")
        overs = overs or kwargs.get("live_overs")
        summary = summary or kwargs.get("live_summary")
        batting = batting or kwargs.get("live_batting")
        bowling = bowling or kwargs.get("live_bowling")
        session = session or kwargs.get("live_session")

        cursor = self.connect()
        cursor.execute("""
            UPDATE live_fixtures
            SET status = COALESCE(?, status),
                live_score_a = COALESCE(?, live_score_a),
                live_score_b = COALESCE(?, live_score_b),
                live_overs = COALESCE(?, live_overs),
                live_summary = COALESCE(?, live_summary),
                live_batting = COALESCE(?, live_batting),
                live_bowling = COALESCE(?, live_bowling),
                live_session = COALESCE(?, live_session)
            WHERE match_id = ?;
        """, [status, score_a, score_b, overs, summary, batting, bowling, session, match_id])

    def add_prediction_audit_entry(
        self,
        prediction_id: str,
        match_id: str,
        match_date: str,
        fmt: str,
        team_a: str,
        team_b: str,
        predicted_winner: str,
        predicted_prob_a: float,
        predicted_prob_b: float,
        score_floor: int,
        score_median: int,
        score_ceil: int,
        actual_winner: str,
        actual_score: int,
        status: str,
        is_hit: bool,
        confidence: float,
        rationale: str
    ) -> None:
        """Appends a completed, verified prediction into the audit log."""
        cursor = self.connect()
        cursor.execute("""
            INSERT OR REPLACE INTO prediction_audit_log VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            );
        """, [
            prediction_id, match_id, match_date, fmt, team_a, team_b,
            predicted_winner, predicted_prob_a, predicted_prob_b,
            score_floor, score_median, score_ceil,
            actual_winner, actual_score, status, is_hit, confidence, rationale
        ])
