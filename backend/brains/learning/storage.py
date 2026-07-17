"""
Trading Market AI
Learning Brain Storage V2

Production Ready Storage Layer

Responsibilities
----------------
✔ SQLite Connection Manager
✔ Transaction Manager
✔ WAL Mode
✔ Foreign Keys
✔ Database Versioning
✔ Thread Safe Connections
✔ Automatic Schema Initialization

Author : Super Cat
"""

from __future__ import annotations

import json
import sqlite3
import threading

from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional
from datetime import datetime

from .models import (
    PredictionRecord,
    TradeOutcome,
    PatternStatistics,
    StrategyStatistics,
)

# ==========================================================
# Database Information
# ==========================================================

DATABASE_VERSION = 2

DATABASE_NAME = "learning.db"

# ==========================================================
# Storage
# ==========================================================


class LearningStorage:

    """
    Production SQLite Storage

    Features
    --------
    • WAL Mode
    • Foreign Keys
    • Transactions
    • Thread Safe
    • Automatic Schema Migration
    """

    _lock = threading.RLock()

    # ------------------------------------------------------

    def __init__(self, db_path: Optional[str] = None):

        if db_path is None:

            self.db_path = (
                Path(__file__).resolve().parent /
                DATABASE_NAME
            )

        else:

            self.db_path = Path(db_path)

        self.initialize()

    # ------------------------------------------------------
    # Connection
    # ------------------------------------------------------

    def connect(self) -> sqlite3.Connection:

        conn = sqlite3.connect(

            self.db_path,

            detect_types=sqlite3.PARSE_DECLTYPES,

            check_same_thread=False,

        )

        conn.row_factory = sqlite3.Row

        # Enable Foreign Keys

        conn.execute("PRAGMA foreign_keys = ON")

        # Better Performance

        conn.execute("PRAGMA journal_mode=WAL")

        conn.execute("PRAGMA synchronous=NORMAL")

        conn.execute("PRAGMA temp_store=MEMORY")

        conn.execute("PRAGMA cache_size=-20000")

        return conn

    # ------------------------------------------------------
    # Transaction
    # ------------------------------------------------------

    @contextmanager

    def transaction(self) -> Iterator[sqlite3.Connection]:

        conn = self.connect()

        try:

            yield conn

            conn.commit()

        except Exception:

            conn.rollback()

            raise

        finally:

            conn.close()

    # ------------------------------------------------------
    # Execute
    # ------------------------------------------------------

    def execute(

        self,

        sql: str,

        parameters: tuple = (),

    ):

        with self.transaction() as conn:

            cursor = conn.execute(

                sql,

                parameters,

            )

            return cursor

    # ------------------------------------------------------
    # Execute Many
    # ------------------------------------------------------

    def executemany(

        self,

        sql: str,

        values,

    ):

        with self.transaction() as conn:

            conn.executemany(

                sql,

                values,

            )

    # ------------------------------------------------------
    # Fetch One
    # ------------------------------------------------------

    def fetchone(

        self,

        sql: str,

        parameters=(),

    ):

        with self.transaction() as conn:

            row = conn.execute(

                sql,

                parameters,

            ).fetchone()

            return row

    # ------------------------------------------------------
    # Fetch All
    # ------------------------------------------------------

    def fetchall(

        self,

        sql: str,

        parameters=(),

    ):

        with self.transaction() as conn:

            rows = conn.execute(

                sql,

                parameters,

            ).fetchall()

            return rows

    # ------------------------------------------------------
    # Initialize
    # ------------------------------------------------------

    def initialize(self):

        """
        Initialize database.

        Creates schema if database
        does not exist.

        Future versions
        automatically migrate schema.
        """

        self.create_metadata_table()

        self.create_schema()

        self.create_indexes()

    # ======================================================
    # Metadata
    # ======================================================

    def create_metadata_table(self):
        """
        Stores database version and future metadata.
        """

        sql = """
        CREATE TABLE IF NOT EXISTS metadata(

            key TEXT PRIMARY KEY,

            value TEXT NOT NULL

        )
        """

        self.execute(sql)

        version = self.fetchone(
            "SELECT value FROM metadata WHERE key='db_version'"
        )

        if version is None:

            self.execute(
                """
                INSERT INTO metadata(key,value)
                VALUES(?,?)
                """,
                (
                    "db_version",
                    str(DATABASE_VERSION),
                ),
            )

    # ======================================================
    # Schema
    # ======================================================

    def create_schema(self):

        """
        Create all Learning Brain tables.
        """

        # --------------------------------------------------
        # Predictions
        # --------------------------------------------------

        self.execute(
            """
            CREATE TABLE IF NOT EXISTS predictions(

                prediction_id TEXT PRIMARY KEY,

                timestamp TEXT NOT NULL,

                symbol TEXT NOT NULL,

                timeframe TEXT,

                current_price REAL,

                decision TEXT,

                confidence REAL,

                price_action_signal TEXT,

                live_market_signal TEXT,

                options_signal TEXT,

                global_market_signal TEXT,

                support REAL,

                resistance REAL,

                atr REAL,

                vix REAL,

                trend TEXT,

                reason TEXT,

                extra_json TEXT

            )
            """
        )

        # --------------------------------------------------
        # Trade Outcomes
        # --------------------------------------------------

        self.execute(
            """
            CREATE TABLE IF NOT EXISTS trade_outcomes(

                prediction_id TEXT PRIMARY KEY,

                entry_price REAL,

                exit_price REAL,

                quantity INTEGER,

                holding_minutes REAL,

                exit_reason TEXT,

                profit_points REAL,

                pnl REAL,

                success INTEGER,

                timestamp TEXT,

                FOREIGN KEY(prediction_id)

                    REFERENCES predictions(prediction_id)

                    ON DELETE CASCADE

            )
            """
        )

        # --------------------------------------------------
        # Pattern Statistics
        # --------------------------------------------------

        self.execute(
            """
            CREATE TABLE IF NOT EXISTS patterns(

                pattern_id TEXT PRIMARY KEY,

                pattern_key TEXT UNIQUE,

                description TEXT,

                occurrences INTEGER,

                wins INTEGER,

                losses INTEGER,

                average_profit REAL,

                average_loss REAL,

                win_rate REAL,

                last_seen TEXT

            )
            """
        )

        # --------------------------------------------------
        # Strategy Statistics
        # --------------------------------------------------

        self.execute(
            """
            CREATE TABLE IF NOT EXISTS strategies(

                strategy_name TEXT PRIMARY KEY,

                total_trades INTEGER,

                wins INTEGER,

                losses INTEGER,

                win_rate REAL,

                average_profit REAL,

                average_loss REAL

            )
            """
        )

        # --------------------------------------------------
        # Brain Weights
        # --------------------------------------------------

        self.execute(
            """
            CREATE TABLE IF NOT EXISTS brain_weights(

                brain_name TEXT PRIMARY KEY,

                weight REAL,

                accuracy REAL,

                total_predictions INTEGER,

                correct_predictions INTEGER,

                last_updated TEXT

            )
            """
        )

    # ======================================================
    # Indexes
    # ======================================================

    def create_indexes(self):

        """
        Create indexes for fast searching.
        """

        indexes = [

            """
            CREATE INDEX IF NOT EXISTS idx_prediction_symbol
            ON predictions(symbol)
            """,

            """
            CREATE INDEX IF NOT EXISTS idx_prediction_time
            ON predictions(timestamp)
            """,

            """
            CREATE INDEX IF NOT EXISTS idx_prediction_decision
            ON predictions(decision)
            """,

            """
            CREATE INDEX IF NOT EXISTS idx_prediction_confidence
            ON predictions(confidence)
            """,

            """
            CREATE INDEX IF NOT EXISTS idx_prediction_trend
            ON predictions(trend)
            """,

            """
            CREATE INDEX IF NOT EXISTS idx_prediction_timeframe
            ON predictions(timeframe)
            """,

            """
            CREATE INDEX IF NOT EXISTS idx_pattern_key
            ON patterns(pattern_key)
            """,

            """
            CREATE INDEX IF NOT EXISTS idx_trade_success
            ON trade_outcomes(success)
            """,

            """
            CREATE INDEX IF NOT EXISTS idx_trade_profit
            ON trade_outcomes(pnl)
            """

        ]

        for sql in indexes:

            self.execute(sql)

    # ======================================================
    # Database Version
    # ======================================================

    def database_version(self) -> int:

        row = self.fetchone(

            """
            SELECT value

            FROM metadata

            WHERE key='db_version'
            """

        )

        if row is None:

            return 1

        return int(row["value"])

    # ======================================================
    # Migration
    # ======================================================

    def migrate(self):

        """
        Future schema migration.

        Example

        Version 2 -> Version 3
        """

        version = self.database_version()

        if version < DATABASE_VERSION:

            print(
                f"Migrating database "
                f"{version} -> {DATABASE_VERSION}"
            )

            self.execute(

                """
                UPDATE metadata

                SET value=?

                WHERE key='db_version'
                """,

                (str(DATABASE_VERSION),)

            )

    # ======================================================
    # Prediction Repository
    # ======================================================

    def save_prediction(
        self,
        prediction: PredictionRecord,
    ) -> None:
        """
        Save or update a prediction.
        """

        sql = """
        INSERT OR REPLACE INTO predictions (

            prediction_id,
            timestamp,
            symbol,
            timeframe,
            current_price,
            decision,
            confidence,
            price_action_signal,
            live_market_signal,
            options_signal,
            global_market_signal,
            support,
            resistance,
            atr,
            vix,
            trend,
            reason,
            extra_json

        )
        VALUES(
            ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?
        )
        """

        self.execute(
            sql,
            (
                prediction.prediction_id,
                prediction.timestamp.isoformat(),
                prediction.symbol,
                prediction.timeframe,
                prediction.current_price,
                prediction.decision,
                prediction.confidence,
                prediction.price_action_signal,
                prediction.live_market_signal,
                prediction.options_signal,
                prediction.global_market_signal,
                prediction.support,
                prediction.resistance,
                prediction.atr,
                prediction.vix,
                prediction.trend,
                prediction.reason,
                json.dumps(prediction.extra),
            ),
        )

    # ======================================================
    # Get Prediction
    # ======================================================

    def get_prediction(
        self,
        prediction_id: str,
    ) -> PredictionRecord | None:

        row = self.fetchone(
            """
            SELECT *

            FROM predictions

            WHERE prediction_id=?
            """,
            (prediction_id,),
        )

        if row is None:
            return None

        return self._prediction_from_row(row)

    # ======================================================
    # Delete Prediction
    # ======================================================

    def delete_prediction(
        self,
        prediction_id: str,
    ):

        self.execute(
            """
            DELETE FROM predictions

            WHERE prediction_id=?
            """,
            (prediction_id,),
        )

    # ======================================================
    # Prediction Exists
    # ======================================================

    def prediction_exists(
        self,
        prediction_id: str,
    ) -> bool:

        row = self.fetchone(
            """
            SELECT COUNT(*)

            AS total

            FROM predictions

            WHERE prediction_id=?
            """,
            (prediction_id,),
        )

        return row["total"] > 0

    # ======================================================
    # Prediction Count
    # ======================================================

    def prediction_count(self) -> int:

        row = self.fetchone(
            """
            SELECT COUNT(*) AS total

            FROM predictions
            """
        )

        return row["total"]

    # ======================================================
    # Recent Predictions
    # ======================================================

    def recent_predictions(
        self,
        limit: int = 50,
    ) -> list[PredictionRecord]:

        rows = self.fetchall(
            """
            SELECT *

            FROM predictions

            ORDER BY timestamp DESC

            LIMIT ?
            """,
            (limit,),
        )

        return [

            self._prediction_from_row(row)

            for row in rows

        ]

    # ======================================================
    # Symbol History
    # ======================================================

    def symbol_history(
        self,
        symbol: str,
        limit: int = 100,
    ) -> list[PredictionRecord]:

        rows = self.fetchall(
            """
            SELECT *

            FROM predictions

            WHERE symbol=?

            ORDER BY timestamp DESC

            LIMIT ?
            """,
            (
                symbol,
                limit,
            ),
        )

        return [

            self._prediction_from_row(row)

            for row in rows

        ]

    # ======================================================
    # Decision History
    # ======================================================

    def decision_history(
        self,
        decision: str,
    ) -> list[PredictionRecord]:

        rows = self.fetchall(
            """
            SELECT *

            FROM predictions

            WHERE decision=?

            ORDER BY timestamp DESC
            """,
            (decision,),
        )

        return [

            self._prediction_from_row(row)

            for row in rows

        ]

    # ======================================================
    # High Confidence
    # ======================================================

    def high_confidence_predictions(
        self,
        minimum: float = 80.0,
    ) -> list[PredictionRecord]:

        rows = self.fetchall(
            """
            SELECT *

            FROM predictions

            WHERE confidence>=?

            ORDER BY confidence DESC
            """,
            (minimum,),
        )

        return [

            self._prediction_from_row(row)

            for row in rows

        ]

    # ======================================================
    # Prediction Mapper
    # ======================================================

    def _prediction_from_row(
        self,
        row,
    ) -> PredictionRecord:

        return PredictionRecord(

            prediction_id=row["prediction_id"],

            timestamp=datetime.fromisoformat(
                row["timestamp"]
            ),

            symbol=row["symbol"],

            timeframe=row["timeframe"],

            current_price=row["current_price"],

            decision=row["decision"],

            confidence=row["confidence"],

            price_action_signal=row["price_action_signal"],

            live_market_signal=row["live_market_signal"],

            options_signal=row["options_signal"],

            global_market_signal=row["global_market_signal"],

            support=row["support"],

            resistance=row["resistance"],

            atr=row["atr"],

            vix=row["vix"],

            trend=row["trend"],

            reason=row["reason"],

            extra=json.loads(
                row["extra_json"] or "{}"
            ),
        )

    # ======================================================
    # Trade Outcome Repository
    # ======================================================

    def save_trade_outcome(
        self,
        outcome: TradeOutcome,
    ) -> None:
        """
        Save completed trade outcome.
        """

        sql = """
        INSERT OR REPLACE INTO trade_outcomes(

            prediction_id,
            entry_price,
            exit_price,
            quantity,
            holding_minutes,
            exit_reason,
            profit_points,
            pnl,
            success,
            timestamp

        )
        VALUES(
            ?,?,?,?,?,?,?,?,?,?
        )
        """

        self.execute(
            sql,
            (
                outcome.prediction_id,
                outcome.entry_price,
                outcome.exit_price,
                outcome.quantity,
                outcome.holding_minutes,
                outcome.exit_reason,
                outcome.profit_points,
                outcome.pnl,
                int(outcome.success),
                outcome.timestamp.isoformat(),
            ),
        )

    # ======================================================
    # Get Outcome
    # ======================================================

    def get_trade_outcome(
        self,
        prediction_id: str,
    ) -> TradeOutcome | None:

        row = self.fetchone(
            """
            SELECT *

            FROM trade_outcomes

            WHERE prediction_id=?
            """,
            (prediction_id,),
        )

        if row is None:
            return None

        return self._trade_outcome_from_row(row)

    # ======================================================
    # Update Outcome
    # ======================================================

    def update_trade_outcome(
        self,
        outcome: TradeOutcome,
    ):

        self.save_trade_outcome(outcome)

    # ======================================================
    # Delete Outcome
    # ======================================================

    def delete_trade_outcome(
        self,
        prediction_id: str,
    ):

        self.execute(
            """
            DELETE FROM trade_outcomes

            WHERE prediction_id=?
            """,
            (prediction_id,),
        )

    # ======================================================
    # Outcome Count
    # ======================================================

    def outcome_count(self) -> int:

        row = self.fetchone(
            """
            SELECT COUNT(*) AS total

            FROM trade_outcomes
            """
        )

        return row["total"]

    # ======================================================
    # All Outcomes
    # ======================================================

    def all_trade_outcomes(
        self,
    ) -> list[TradeOutcome]:

        rows = self.fetchall(
            """
            SELECT *

            FROM trade_outcomes

            ORDER BY timestamp DESC
            """
        )

        return [

            self._trade_outcome_from_row(row)

            for row in rows

        ]

    # ======================================================
    # Winning Trades
    # ======================================================

    def winning_trades(
        self,
    ) -> list[TradeOutcome]:

        rows = self.fetchall(
            """
            SELECT *

            FROM trade_outcomes

            WHERE success=1

            ORDER BY pnl DESC
            """
        )

        return [

            self._trade_outcome_from_row(row)

            for row in rows

        ]

    # ======================================================
    # Losing Trades
    # ======================================================

    def losing_trades(
        self,
    ) -> list[TradeOutcome]:

        rows = self.fetchall(
            """
            SELECT *

            FROM trade_outcomes

            WHERE success=0

            ORDER BY pnl ASC
            """
        )

        return [

            self._trade_outcome_from_row(row)

            for row in rows

        ]

    # ======================================================
    # Best Trade
    # ======================================================

    def best_trade(
        self,
    ) -> TradeOutcome | None:

        row = self.fetchone(
            """
            SELECT *

            FROM trade_outcomes

            ORDER BY pnl DESC

            LIMIT 1
            """
        )

        if row is None:
            return None

        return self._trade_outcome_from_row(row)

    # ======================================================
    # Worst Trade
    # ======================================================

    def worst_trade(
        self,
    ) -> TradeOutcome | None:

        row = self.fetchone(
            """
            SELECT *

            FROM trade_outcomes

            ORDER BY pnl ASC

            LIMIT 1
            """
        )

        if row is None:
            return None

        return self._trade_outcome_from_row(row)

    # ======================================================
    # Trade Outcome Mapper
    # ======================================================

    def _trade_outcome_from_row(
        self,
        row,
    ) -> TradeOutcome:

        return TradeOutcome(

            prediction_id=row["prediction_id"],

            entry_price=row["entry_price"],

            exit_price=row["exit_price"],

            quantity=row["quantity"],

            holding_minutes=row["holding_minutes"],

            exit_reason=row["exit_reason"],

            profit_points=row["profit_points"],

            pnl=row["pnl"],

            success=bool(row["success"]),

            timestamp=datetime.fromisoformat(
                row["timestamp"]
            ),
        )

    # ======================================================
    # Pattern Repository
    # ======================================================

    def save_pattern(
        self,
        pattern: PatternStatistics,
    ) -> None:
        """
        Save pattern statistics.
        """

        sql = """
        INSERT OR REPLACE INTO patterns(

            pattern_id,

            pattern_key,

            description,

            occurrences,

            wins,

            losses,

            average_profit,

            average_loss,

            win_rate,

            last_seen

        )

        VALUES(

            ?,?,?,?,?,?,?,?,?,?

        )
        """

        self.execute(

            sql,

            (

                pattern.pattern_id,

                pattern.pattern_key,

                pattern.description,

                pattern.occurrences,

                pattern.wins,

                pattern.losses,

                pattern.average_profit,

                pattern.average_loss,

                pattern.win_rate,

                pattern.last_seen,

            ),

        )

    # ======================================================
    # Get Pattern
    # ======================================================

    def get_pattern(

        self,

        pattern_id: str,

    ) -> PatternStatistics | None:

        row = self.fetchone(

            """

            SELECT *

            FROM patterns

            WHERE pattern_id=?

            """,

            (pattern_id,),

        )

        if row is None:

            return None

        return self._pattern_from_row(row)

    # ======================================================
    # Pattern Exists
    # ======================================================

    def pattern_exists(

        self,

        pattern_key: str,

    ) -> bool:

        row = self.fetchone(

            """

            SELECT COUNT(*) AS total

            FROM patterns

            WHERE pattern_key=?

            """,

            (pattern_key,),

        )

        return row["total"] > 0

    # ======================================================
    # Find Pattern
    # ======================================================

    def find_pattern(

        self,

        pattern_key: str,

    ) -> PatternStatistics | None:

        row = self.fetchone(

            """

            SELECT *

            FROM patterns

            WHERE pattern_key=?

            """,

            (pattern_key,),

        )

        if row is None:

            return None

        return self._pattern_from_row(row)

    # ======================================================
    # Update Pattern
    # ======================================================

    def update_pattern(

        self,

        pattern: PatternStatistics,

    ):

        self.save_pattern(pattern)

    # ======================================================
    # Delete Pattern
    # ======================================================

    def delete_pattern(

        self,

        pattern_id: str,

    ):

        self.execute(

            """

            DELETE FROM patterns

            WHERE pattern_id=?

            """,

            (pattern_id,),

        )

    # ======================================================
    # Pattern Count
    # ======================================================

    def pattern_count(self) -> int:

        row = self.fetchone(

            """

            SELECT COUNT(*) AS total

            FROM patterns

            """

        )

        return row["total"]

    # ======================================================
    # Top Patterns
    # ======================================================

    def top_patterns(

        self,

        limit: int = 20,

    ) -> list[PatternStatistics]:

        rows = self.fetchall(

            """

            SELECT *

            FROM patterns

            ORDER BY win_rate DESC,

                     occurrences DESC

            LIMIT ?

            """,

            (limit,),

        )

        return [

            self._pattern_from_row(row)

            for row in rows

        ]

    # ======================================================
    # Most Frequent Patterns
    # ======================================================

    def frequent_patterns(

        self,

        limit: int = 20,

    ) -> list[PatternStatistics]:

        rows = self.fetchall(

            """

            SELECT *

            FROM patterns

            ORDER BY occurrences DESC

            LIMIT ?

            """,

            (limit,),

        )

        return [

            self._pattern_from_row(row)

            for row in rows

        ]

    # ======================================================
    # Pattern Mapper
    # ======================================================

    def _pattern_from_row(

        self,

        row,

    ) -> PatternStatistics:

        return PatternStatistics(

            pattern_id=row["pattern_id"],

            pattern_key=row["pattern_key"],

            description=row["description"],

            total_occurrences=row["occurrences"],

            wins=row["wins"],

            losses=row["losses"],

            average_profit=row["average_profit"],

            average_loss=row["average_loss"],

            win_rate=row["win_rate"],

        )

    # ======================================================
    # Statistics Repository
    # ======================================================

    def total_predictions(self) -> int:

        return self.prediction_count()

    # ------------------------------------------------------

    def total_completed_trades(self) -> int:

        return self.outcome_count()

    # ------------------------------------------------------

    def total_wins(self) -> int:

        row = self.fetchone(

            """
            SELECT COUNT(*) AS total

            FROM trade_outcomes

            WHERE success=1
            """

        )

        return row["total"]

    # ------------------------------------------------------

    def total_losses(self) -> int:

        row = self.fetchone(

            """
            SELECT COUNT(*) AS total

            FROM trade_outcomes

            WHERE success=0
            """

        )

        return row["total"]

    # ------------------------------------------------------

    def win_rate(self) -> float:

        total = self.total_completed_trades()

        if total == 0:

            return 0.0

        return round(

            (self.total_wins() / total) * 100,

            2,

        )

    # ------------------------------------------------------

    def total_profit(self) -> float:

        row = self.fetchone(

            """
            SELECT

            COALESCE(SUM(pnl),0)

            AS pnl

            FROM trade_outcomes
            """

        )

        return float(row["pnl"])

    # ------------------------------------------------------

    def average_profit(self) -> float:

        row = self.fetchone(

            """
            SELECT

            COALESCE(AVG(pnl),0)

            AS avg_profit

            FROM trade_outcomes
            """

        )

        return round(

            float(row["avg_profit"]),

            2,

        )

    # ------------------------------------------------------

    def average_holding_time(self) -> float:

        row = self.fetchone(

            """
            SELECT

            COALESCE(AVG(holding_minutes),0)

            AS holding

            FROM trade_outcomes
            """

        )

        return round(

            float(row["holding"]),

            2,

        )

    # ------------------------------------------------------

    def biggest_profit(self):

        return self.best_trade()

    # ------------------------------------------------------

    def biggest_loss(self):

        return self.worst_trade()

    # ------------------------------------------------------

    def dashboard_statistics(self):

        """
        Dashboard summary.

        One function for entire dashboard.
        """

        return {

            "predictions":
                self.total_predictions(),

            "completed_trades":
                self.total_completed_trades(),

            "wins":
                self.total_wins(),

            "losses":
                self.total_losses(),

            "win_rate":
                self.win_rate(),

            "total_profit":
                self.total_profit(),

            "average_profit":
                self.average_profit(),

            "average_holding":
                self.average_holding_time(),

            "patterns":
                self.pattern_count(),

        }

    # ======================================================
    # Advanced Search
    # ======================================================

    def search_predictions(

        self,

        symbol=None,

        decision=None,

        trend=None,

        minimum_confidence=None,

        timeframe=None,

    ):

        sql = "SELECT * FROM predictions WHERE 1=1"

        params = []

        if symbol:

            sql += " AND symbol=?"

            params.append(symbol)

        if decision:

            sql += " AND decision=?"

            params.append(decision)

        if trend:

            sql += " AND trend=?"

            params.append(trend)

        if minimum_confidence is not None:

            sql += " AND confidence>=?"

            params.append(minimum_confidence)

        if timeframe:

            sql += " AND timeframe=?"

            params.append(timeframe)

        sql += " ORDER BY timestamp DESC"

        rows = self.fetchall(

            sql,

            tuple(params),

        )

        return [

            self._prediction_from_row(row)

            for row in rows

        ]

    # ======================================================
    # Database Maintenance
    # ======================================================

    def vacuum(self):
        """
        Rebuild database and reclaim unused space.
        """

        with self.connect() as conn:
            conn.execute("VACUUM")

    # ------------------------------------------------------

    def analyze(self):
        """
        Update SQLite query planner statistics.
        """

        with self.connect() as conn:
            conn.execute("ANALYZE")

    # ------------------------------------------------------

    def optimize(self):
        """
        Optimize database.
        """

        self.vacuum()

        self.analyze()

    # ======================================================
    # Backup
    # ======================================================

    def backup(self, destination: str):

        destination = Path(destination)

        source = self.connect()

        backup = sqlite3.connect(destination)

        with backup:

            source.backup(backup)

        backup.close()

        source.close()

    # ======================================================
    # Restore
    # ======================================================

    def restore(self, backup_file: str):

        backup_file = Path(backup_file)

        if not backup_file.exists():

            raise FileNotFoundError(backup_file)

        source = sqlite3.connect(backup_file)

        destination = self.connect()

        with destination:

            source.backup(destination)

        source.close()

        destination.close()

    # ======================================================
    # Database Size
    # ======================================================

    def database_size(self) -> int:

        return self.db_path.stat().st_size

    # ======================================================
    # Database Information
    # ======================================================

    def database_info(self):

        return {

            "database": str(self.db_path),

            "version": self.database_version(),

            "size_bytes": self.database_size(),

            "predictions": self.prediction_count(),

            "outcomes": self.outcome_count(),

            "patterns": self.pattern_count(),

        }

    # ======================================================
    # Clear Tables
    # ======================================================

    def clear_predictions(self):

        self.execute(

            "DELETE FROM predictions"

        )

    # ------------------------------------------------------

    def clear_trade_outcomes(self):

        self.execute(

            "DELETE FROM trade_outcomes"

        )

    # ------------------------------------------------------

    def clear_patterns(self):

        self.execute(

            "DELETE FROM patterns"

        )

    # ------------------------------------------------------

    def clear_strategies(self):

        self.execute(

            "DELETE FROM strategies"

        )

    # ------------------------------------------------------

    def clear_brain_weights(self):

        self.execute(

            "DELETE FROM brain_weights"

        )

    # ======================================================
    # Reset Database
    # ======================================================

    def reset_database(self):
        """
        Deletes all learning data.
        """

        with self.transaction() as conn:

            conn.execute("DELETE FROM trade_outcomes")

            conn.execute("DELETE FROM predictions")

            conn.execute("DELETE FROM patterns")

            conn.execute("DELETE FROM strategies")

            conn.execute("DELETE FROM brain_weights")

