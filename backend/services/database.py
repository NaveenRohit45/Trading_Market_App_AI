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

    def conn(self): return sqlite3.connect(self.path)

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

    def history(self, limit=100):
        with self.conn() as c:
            c.row_factory = sqlite3.Row
            return [dict(r) for r in c.execute("SELECT * FROM predictions ORDER BY id DESC LIMIT ?",(limit,))]

    def accuracy(self):
        with self.conn() as c:
            rows = c.execute("SELECT symbol,horizon,COUNT(*),SUM(correct) FROM predictions WHERE resolved=1 GROUP BY symbol,horizon").fetchall()
        return [{"symbol":r[0],"horizon":r[1],"count":r[2],"accuracy":round(100*(r[3] or 0)/r[2],1)} for r in rows]
