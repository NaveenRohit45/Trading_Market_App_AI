import sqlite3, json
from pathlib import Path

class Database:
    def __init__(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.path = str(path)
        with self.conn() as c:
            c.execute('''CREATE TABLE IF NOT EXISTS predictions(
              id INTEGER PRIMARY KEY AUTOINCREMENT, ts REAL, symbol TEXT, horizon INTEGER,
              price REAL, direction TEXT, confidence REAL, payload TEXT,
              features TEXT,
              resolved INTEGER DEFAULT 0, actual_direction TEXT, correct INTEGER)''')
            # Add the column if the DB already existed from before this change.
            try:
                c.execute("ALTER TABLE predictions ADD COLUMN features TEXT")
            except sqlite3.OperationalError:
                pass

            # Raw 1-minute candle history -- needed for the LSTM
            # (train_lstm.py) which learns from candle SEQUENCES, not
            # single snapshots like the RandomForest does.
            c.execute('''CREATE TABLE IF NOT EXISTS candles(
              symbol TEXT, ts REAL, open REAL, high REAL, low REAL,
              close REAL, volume REAL,
              PRIMARY KEY (symbol, ts))''')

            # Per-brain call tracking -- this is what lets the
            # Confidence Engine adapt itself instead of using fixed
            # weights forever. Every brain's directional call gets
            # logged here and resolved the same way predictions are,
            # so we can compute EACH BRAIN'S OWN rolling accuracy.
            c.execute('''CREATE TABLE IF NOT EXISTS brain_calls(
              id INTEGER PRIMARY KEY AUTOINCREMENT, ts REAL, symbol TEXT,
              brain TEXT, horizon INTEGER, price REAL, direction TEXT,
              regime TEXT, context TEXT, failure_reasons TEXT,
              resolved INTEGER DEFAULT 0, actual_direction TEXT, correct INTEGER)''')
            # Add columns if the DB already existed before this change.
            for col in ("context", "failure_reasons"):
                try:
                    c.execute(f"ALTER TABLE brain_calls ADD COLUMN {col} TEXT")
                except sqlite3.OperationalError:
                    pass

    def conn(self): return sqlite3.connect(self.path)

    def add_candle(self, symbol, ts, open_, high, low, close, volume=0.0):
        with self.conn() as c:
            c.execute(
                "INSERT OR IGNORE INTO candles(symbol,ts,open,high,low,close,volume) VALUES(?,?,?,?,?,?,?)",
                (symbol, ts, open_, high, low, close, volume),
            )

    def add_prediction(self, ts, symbol, horizon, price, pred, features=None):
        with self.conn() as c:
            c.execute("INSERT INTO predictions(ts,symbol,horizon,price,direction,confidence,payload,features) VALUES(?,?,?,?,?,?,?,?)",
                      (ts,symbol,horizon,price,pred["direction"],pred["confidence"],json.dumps(pred),
                       json.dumps(features) if features else None))

    def resolve(self, now, prices):
        with self.conn() as c:
            rows = c.execute("SELECT id,ts,symbol,horizon,price,direction FROM predictions WHERE resolved=0").fetchall()
            for rid,ts,sym,h,p0,direction in rows:
                if now-ts >= h*60 and sym in prices:
                    p1 = prices[sym]
                    pct = (p1-p0)/p0*100 if p0 else 0
                    actual = "UP" if pct > 0.03 else "DOWN" if pct < -0.03 else "SIDEWAYS"
                    c.execute("UPDATE predictions SET resolved=1,actual_direction=?,correct=? WHERE id=?",
                              (actual, int(actual==direction), rid))

    def add_brain_call(self, ts, symbol, brain, horizon, price, direction, regime=None, context=None):
        with self.conn() as c:
            c.execute(
                "INSERT INTO brain_calls(ts,symbol,brain,horizon,price,direction,regime,context) VALUES(?,?,?,?,?,?,?,?)",
                (ts, symbol, brain, horizon, price, direction, regime,
                 json.dumps(context) if context else None),
            )

    def resolve_brain_calls(self, now, prices):
        from backend.analyzers.failure_reasons import compute_failure_reasons

        with self.conn() as c:
            rows = c.execute(
                "SELECT id,ts,symbol,horizon,price,direction,context FROM brain_calls WHERE resolved=0"
            ).fetchall()
            for rid, ts, sym, h, p0, direction, context_json in rows:
                if now - ts >= h * 60 and sym in prices:
                    p1 = prices[sym]
                    pct = (p1 - p0) / p0 * 100 if p0 else 0
                    actual = "UP" if pct > 0.03 else "DOWN" if pct < -0.03 else "SIDEWAYS"
                    correct = int(actual == direction)

                    failure_reasons_json = None
                    if not correct and context_json:
                        try:
                            context = json.loads(context_json)
                            reasons = compute_failure_reasons(direction, context)
                            failure_reasons_json = json.dumps(reasons)
                        except (json.JSONDecodeError, TypeError):
                            pass

                    c.execute(
                        "UPDATE brain_calls SET resolved=1,actual_direction=?,correct=?,failure_reasons=? WHERE id=?",
                        (actual, correct, failure_reasons_json, rid),
                    )

    def failure_reason_stats(self, symbol=None, min_occurrences=3):
        """
        THE query that answers "never buy when resistance + high vol +
        negative news" -- counts how often each failure-reason
        COMBINATION shows up across actual wrong calls, and its
        overall win rate when that combination was present (including
        the times it happened to still be right).
        """
        query = "SELECT direction, failure_reasons, correct FROM brain_calls WHERE resolved=1 AND failure_reasons IS NOT NULL"
        params = []
        if symbol:
            query += " AND symbol=?"
            params.append(symbol)

        with self.conn() as c:
            rows = c.execute(query, params).fetchall()

        combo_stats = {}
        for direction, reasons_json, correct in rows:
            try:
                reasons = tuple(sorted(json.loads(reasons_json)))
            except (json.JSONDecodeError, TypeError):
                continue
            if not reasons:
                continue
            key = (direction, reasons)
            combo_stats.setdefault(key, {"wrong": 0, "total": 0})
            combo_stats[key]["total"] += 1
            if not correct:
                combo_stats[key]["wrong"] += 1

        results = []
        for (direction, reasons), stats in combo_stats.items():
            if stats["total"] < min_occurrences:
                continue
            results.append({
                "direction": direction,
                "reasons": list(reasons),
                "occurrences": stats["total"],
                "failure_rate": round(100 * stats["wrong"] / stats["total"], 1),
            })

        results.sort(key=lambda r: r["failure_rate"], reverse=True)
        return results

    def brain_accuracy(self, symbol=None, regime=None, lookback=100):
        """
        Rolling accuracy per brain -- the actual numbers the Adaptive
        Confidence Engine uses to reweight itself. Optionally filtered
        by symbol and/or market regime, since a brain that is great in
        a trending market may be bad in a ranging one.
        """
        query = "SELECT brain, direction, actual_direction, correct, ts FROM brain_calls WHERE resolved=1"
        params = []
        if symbol:
            query += " AND symbol=?"
            params.append(symbol)
        if regime:
            query += " AND regime=?"
            params.append(regime)
        query += " ORDER BY ts DESC"

        with self.conn() as c:
            rows = c.execute(query, params).fetchall()

        per_brain = {}
        for brain, direction, actual, correct, ts in rows:
            per_brain.setdefault(brain, []).append(correct)

        results = {}
        for brain, outcomes in per_brain.items():
            recent = outcomes[:lookback]
            results[brain] = {
                "accuracy": round(100 * sum(recent) / len(recent), 1) if recent else None,
                "sample_size": len(recent),
            }
        return results

    def history(self, limit=100):
        with self.conn() as c:
            c.row_factory = sqlite3.Row
            return [dict(r) for r in c.execute("SELECT * FROM predictions ORDER BY id DESC LIMIT ?",(limit,))]

    def accuracy(self):
        with self.conn() as c:
            rows = c.execute("SELECT symbol,horizon,COUNT(*),SUM(correct) FROM predictions WHERE resolved=1 GROUP BY symbol,horizon").fetchall()
        return [{"symbol":r[0],"horizon":r[1],"count":r[2],"accuracy":round(100*(r[3] or 0)/r[2],1)} for r in rows]

    def replay_session(self, symbol, limit=200):
        """
        For Historical Replay: every resolved prediction for a symbol,
        with what actually happened, ordered oldest-first so the
        frontend can step through a session chronologically.
        """
        with self.conn() as c:
            c.row_factory = sqlite3.Row
            rows = c.execute(
                """
                SELECT ts, symbol, horizon, price, direction, confidence,
                       features, actual_direction, correct
                FROM predictions
                WHERE symbol=? AND resolved=1
                ORDER BY ts ASC
                LIMIT ?
                """,
                (symbol, limit),
            ).fetchall()
        return [dict(r) for r in rows]
