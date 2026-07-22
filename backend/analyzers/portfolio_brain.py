"""
Portfolio / Risk Brain

HONEST FRAMING, up front: this app doesn't place real orders (no
execution layer exists), so this tracks HYPOTHETICAL P/L based on
what would have happened if each resolved prediction had been traded
with a fixed notional size -- not your real account P/L. Treat it as
a risk-discipline simulator: it shows you what following this
system's calls would have done, and enforces the same stop-trading
discipline a real desk would use, so you can see whether that
discipline would have helped BEFORE risking real capital on it.

What it tracks, using real resolved predictions already in the DB:
- Today's and this week's hypothetical P/L
- Maximum drawdown from the running equity curve
- Current win/loss streak
- A STOP_TRADING flag that flips on after N consecutive losses,
  exactly like the "3 losses -> stop trading" rule professional desks
  use to protect capital -- surfaced clearly on the dashboard, not
  silently ignored.
"""

from __future__ import annotations

from datetime import datetime, timedelta

CONSECUTIVE_LOSS_STOP_THRESHOLD = 3
NOTIONAL_PER_TRADE = 1.0  # hypothetical "1 unit" per trade -- P/L is in % terms, not currency


def compute_portfolio_stats(resolved_predictions: list[dict]) -> dict:
    """
    resolved_predictions: rows from database.history() or similar --
    each needs at minimum: ts, symbol, direction, price, correct,
    actual_direction. Ordered oldest-first for a correct equity curve
    and streak calculation.
    """

    if not resolved_predictions:
        return {
            "today_pnl_pct": 0.0,
            "week_pnl_pct": 0.0,
            "max_drawdown_pct": 0.0,
            "current_streak": 0,
            "streak_type": None,
            "win_rate": None,
            "stop_trading": False,
            "total_resolved": 0,
        }

    now = datetime.now()
    today_start = datetime(now.year, now.month, now.day).timestamp()
    week_start = (now - timedelta(days=7)).timestamp()

    equity = 0.0
    peak_equity = 0.0
    max_drawdown = 0.0

    today_pnl = 0.0
    week_pnl = 0.0

    wins = 0
    losses = 0

    current_streak = 0
    streak_type = None

    for row in resolved_predictions:
        # Hypothetical P/L per trade: fixed notional gain/loss based
        # on correct/incorrect, NOT actual point movement -- this
        # measures the SYSTEM's hit-rate discipline, not simulated
        # dollar amounts (which would need real position sizing rules
        # this app doesn't have yet).
        pnl = NOTIONAL_PER_TRADE if row.get("correct") else -NOTIONAL_PER_TRADE

        equity += pnl
        peak_equity = max(peak_equity, equity)
        drawdown = peak_equity - equity
        max_drawdown = max(max_drawdown, drawdown)

        ts = row.get("ts", 0)
        if ts >= today_start:
            today_pnl += pnl
        if ts >= week_start:
            week_pnl += pnl

        if row.get("correct"):
            wins += 1
            if streak_type == "WIN":
                current_streak += 1
            else:
                streak_type = "WIN"
                current_streak = 1
        else:
            losses += 1
            if streak_type == "LOSS":
                current_streak += 1
            else:
                streak_type = "LOSS"
                current_streak = 1

    total = wins + losses
    win_rate = round(100 * wins / total, 1) if total else None

    stop_trading = (
        streak_type == "LOSS"
        and current_streak >= CONSECUTIVE_LOSS_STOP_THRESHOLD
    )

    return {
        "today_pnl_pct": round(today_pnl, 2),
        "week_pnl_pct": round(week_pnl, 2),
        "max_drawdown_pct": round(max_drawdown, 2),
        "current_streak": current_streak,
        "streak_type": streak_type,
        "win_rate": win_rate,
        "stop_trading": stop_trading,
        "total_resolved": total,
    }
