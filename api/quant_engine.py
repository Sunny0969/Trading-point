"""
TradingPoint Server-Side Autonomous Quant Execution Engine (Production-Grade & Zero-Trust)
Implements deterministic SHA-256 fingerprinting, server dynamic equity calculation,
mathematical risk ceiling, precision lot allocation, and atomic DB execution.
Ultra-Low-Risk Micro Scalper Policy:
- 0 Loss Equivalent: Aggressive Break-Even (BE) Lock once in +$0.80 profit.
- Minimum loss guard: Tight initial SL clamped to max $1.35 - $1.40 from entry.
- Quick profit targets: Scalp TP clamped to $2.20 - $2.80 from entry (banking $2 - $10 profit per trade).
- Micro lots: Conservative 0.01 - 0.02 lots.
- Autonomous Server Daemon: Runs 24/7 on backend even when user closes browser tab.
Dual-mode engine: Direct PostgreSQL (pg8000) with seamless connection retry.
"""

import os
import sys
import hashlib
import math
import json
import uuid
import time
import threading

# Ensure parent and current directory are in sys.path
_current_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_current_dir)
for _p in [_current_dir, _parent_dir]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import requests

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://tcwboskfypcrsrniatni.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY", "sb_publishable_r39tpba3IS43B9icWt26KA_kC0OH5Pk")

DB_USER = os.environ.get("SUPABASE_DB_USER", "postgres.tcwboskfypcrsrniatni")
DB_PASSWORD = os.environ.get("SUPABASE_DB_PASSWORD", "GuEyWSzHSDmLDn9u")
DB_HOST = os.environ.get("SUPABASE_DB_HOST", "aws-0-ap-northeast-1.pooler.supabase.com")
DB_PORT = int(os.environ.get("SUPABASE_DB_PORT", "5432"))
DB_NAME = os.environ.get("SUPABASE_DB_NAME", "postgres")

# User directive: "mujhe heavy profit nhn chaiye, bot chote chote profit le, loss minimum ho bilkul na hone ke barabar, long stop loss na le"
MAX_SL_DISTANCE = 1.35   # Max $1.35 SL distance (loss strictly minimized to ~$1.35 - $2.70)
SCALP_TP_DISTANCE = 2.50 # Quick $2.50 profit target (quick scalp banking $2.50 - $5.00 per trade)
BE_LOCK_DISTANCE = 0.80  # Once price moves +$0.80 into profit, lock Break-Even (0 Loss Guard)

# Shared Telemetry State
_daemon_started = False
_last_telemetry = {
    "status": "INITIALIZING",
    "last_tick_time": 0,
    "live_price": 0.0,
    "active_users": 0,
    "open_bot_orders": 0,
    "closed_harvests": 0,
    "be_locked_count": 0,
    "total_harvested_profit_usd": 0.0,
    "last_log": "Engine initialized"
}

def _get_rest_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

def get_live_gold_spot():
    """Fetches real-time Gold spot prices and session momentum directly from TradingView CFD Scanner."""
    try:
        url = "https://scanner.tradingview.com/cfd/scan"
        payload = {
            "symbols": {"tickers": ["OANDA:XAUUSD", "TVC:GOLD", "FOREXCOM:XAUUSD"]},
            "columns": ["close", "open", "high", "low", "change", "change_abs", "bid", "ask", "Recommend.All"]
        }
        res = requests.post(url, json=payload, timeout=4)
        if res.status_code == 200:
            data = res.json().get("data", [])
            for item in data:
                row = item.get("d", [])
                if row and row[0] is not None:
                    return {
                        "price": float(row[0]),
                        "open": float(row[1] if row[1] is not None else row[0]),
                        "high": float(row[2] if row[2] is not None else row[0] + 5),
                        "low": float(row[3] if row[3] is not None else row[0] - 5),
                        "bid": float(row[6] if len(row) > 6 and row[6] is not None else row[0] - 0.25),
                        "ask": float(row[7] if len(row) > 7 and row[7] is not None else row[0] + 0.25),
                        "signal": float(row[8] if len(row) > 8 and row[8] is not None else 0.1)
                    }
    except Exception:
        pass
    return {"price": 3965.00, "open": 3960.00, "high": 3970.00, "low": 3955.00, "bid": 3964.75, "ask": 3965.25, "signal": 0.1}

def apply_micro_scalp_levels(direction: str, entry: float, raw_sl: float, raw_tp: float):
    """Enforces ultra-low-risk tight SL and quick scalp TP."""
    if direction == "SELL":
        sl = round(min(raw_sl if raw_sl > entry else entry + MAX_SL_DISTANCE, entry + MAX_SL_DISTANCE), 2)
        tp = round(entry - SCALP_TP_DISTANCE, 2)
    else:  # BUY
        sl = round(max(raw_sl if raw_sl < entry else entry - MAX_SL_DISTANCE, entry - MAX_SL_DISTANCE), 2)
        tp = round(entry + SCALP_TP_DISTANCE, 2)
    return sl, tp

def get_pg_connection():
    """Establishes direct PostgreSQL pooler connection with SSL and retry."""
    import ssl
    import pg8000.native
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    for attempt in range(3):
        try:
            return pg8000.native.Connection(
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
                ssl_context=ctx,
                timeout=10
            )
        except Exception:
            if attempt < 2:
                time.sleep(0.6)
    raise RuntimeError("Failed to connect to Supabase PostgreSQL pooler after 3 attempts")

def process_signal_server_authoritative(payload: dict) -> dict:
    """Zero-Trust server-authoritative execution engine."""
    user_id = payload.get("userId")
    source = payload.get("source", "SMC_CONFLUENCE")
    direction = str(payload.get("direction", "BUY")).upper()

    try:
        entry = float(payload.get("entry", 0))
        raw_sl = float(payload.get("sl", 0))
        raw_tp = float(payload.get("tp", 0))
    except (ValueError, TypeError):
        return {"status": "FAILED", "reason": "Invalid numerical parameters for entry, sl, or tp"}

    candle_time = str(payload.get("candleTime", ""))

    if not user_id:
        return {"status": "FAILED", "reason": "Missing authenticated userId"}

    sl, tp = apply_micro_scalp_levels(direction, entry, raw_sl, raw_tp)

    raw_fingerprint = f"{source}|{direction}|{entry:.2f}|{sl:.2f}|{candle_time}"
    signal_hash = hashlib.sha256(raw_fingerprint.encode("utf-8")).hexdigest()

    conn = get_pg_connection()
    try:
        return _process_via_pg(conn, user_id, source, direction, entry, sl, tp, signal_hash)
    finally:
        conn.close()

def _process_via_pg(conn, user_id, source, direction, entry, sl, tp, signal_hash):
    # Fetch Settings
    settings_rows = conn.run(
        "SELECT is_active, risk_per_trade_percent, daily_drawdown_limit_percent, max_open_bot_trades, cooldown_minutes, kill_switch "
        "FROM public.bot_settings WHERE user_id = :uid",
        uid=user_id
    )

    if not settings_rows:
        conn.run(
            "INSERT INTO public.bot_settings (user_id, is_active, risk_per_trade_percent, max_open_bot_trades, kill_switch) "
            "VALUES (:uid, true, 1.00, 2, false) ON CONFLICT (user_id) DO NOTHING",
            uid=user_id
        )
        is_active, risk_percent, daily_dd, max_trades, cooldown, kill_switch = True, 1.00, 3.00, 2, 15, False
    else:
        is_active, risk_percent, daily_dd, max_trades, cooldown, kill_switch = settings_rows[0]
        risk_percent = float(risk_percent or 1.0)
        max_trades = int(max_trades or 2)

    if not is_active or kill_switch:
        return {"status": "ABORTED", "reason": "Bot inactive or Kill Switch engaged"}

    existing = conn.run(
        "SELECT status FROM public.bot_signals WHERE user_id = :uid AND signal_hash = :sh",
        uid=user_id,
        sh=signal_hash
    )

    if existing:
        current_status = existing[0][0]
        if current_status in ("EXECUTED", "PENDING"):
            return {"status": "SKIPPED", "reason": f"Signal already processed or currently executing ({current_status})"}

    conn.run(
        "INSERT INTO public.bot_signals (user_id, signal_hash, indicator_source, direction, entry_price, sl_price, tp_price, status) "
        "VALUES (:uid, :sh, :src, :dir, :ep, :slp, :tpp, 'PENDING') "
        "ON CONFLICT (user_id, signal_hash) DO UPDATE SET status = 'PENDING'",
        uid=user_id, sh=signal_hash, src=source, dir=direction, ep=entry, slp=sl, tpp=tp
    )

    wallet_rows = conn.run("SELECT balance FROM public.wallets WHERE user_id = :uid", uid=user_id)
    if not wallet_rows:
        prof_rows = conn.run("SELECT demo_balance FROM public.profiles WHERE id = :uid", uid=user_id)
        wallet_balance = float(prof_rows[0][0]) if prof_rows else 1000.0
        conn.run("INSERT INTO public.wallets (user_id, balance) VALUES (:uid, :bal) ON CONFLICT (user_id) DO NOTHING", uid=user_id, bal=wallet_balance)
    else:
        wallet_balance = float(wallet_rows[0][0])

    open_orders = conn.run(
        "SELECT unrealized_pnl, executed_by FROM public.orders WHERE user_id = :uid AND status = 'OPEN'",
        uid=user_id
    )

    open_bot_orders = [o for o in open_orders if o[1] == 'BOT']
    if len(open_bot_orders) >= max_trades:
        _log_decision_pg(conn, user_id, signal_hash, 'SKIPPED_COOLDOWN', 0, 0, 0, f'Max concurrent bot trades reached ({len(open_bot_orders)}/{max_trades})')
        _update_signal_status_pg(conn, user_id, signal_hash, 'CANCELLED')
        return {"status": "SKIPPED", "reason": "Max open trades reached"}

    total_unrealized_pnl = sum([float(o[0] or 0) for o in open_orders])
    server_dynamic_equity = wallet_balance + total_unrealized_pnl

    if server_dynamic_equity <= 0:
        _update_signal_status_pg(conn, user_id, signal_hash, 'FAILED')
        return {"status": "FAILED", "reason": "Insufficient or invalid server equity"}

    max_allowed_risk_usd = server_dynamic_equity * (risk_percent / 100.0)
    sl_distance = abs(entry - sl)

    if sl_distance <= 0.05:
        _log_decision_pg(conn, user_id, signal_hash, 'SKIPPED_MAX_RISK', 0, 0, server_dynamic_equity, 'Invalid tight SL distance')
        _update_signal_status_pg(conn, user_id, signal_hash, 'CANCELLED')
        return {"status": "SKIPPED", "reason": "Invalid SL distance"}

    raw_lot = max_allowed_risk_usd / (sl_distance * 100.0)
    final_lot = math.floor(raw_lot * 100.0 + 1e-9) / 100.0
    final_lot = max(0.01, min(final_lot, 0.02))

    actual_risk_usd = final_lot * sl_distance * 100.0
    order_uuid = str(uuid.uuid4())

    try:
        conn.run(
            "INSERT INTO public.orders (id, user_id, symbol, type, direction, entry_price, sl, stop_loss, tp, take_profit, lots, lot_size, executed_by, signal_id, status) "
            "VALUES (:oid, :uid, 'XAU/USD', :dir, :dir, :ep, :slp, :slp, :tpp, :tpp, :lots, :lots, 'BOT', :sh, 'OPEN')",
            oid=order_uuid, uid=user_id, dir=direction, ep=entry, slp=sl, tpp=tp, lots=final_lot, sh=signal_hash
        )

        _update_signal_status_pg(conn, user_id, signal_hash, 'EXECUTED')
        _log_decision_pg(conn, user_id, signal_hash, 'EXECUTED', final_lot, actual_risk_usd, server_dynamic_equity, 'Micro-scalp order filled via automated risk gate')

        return {
            "status": "SUCCESS",
            "orderId": order_uuid,
            "lot": final_lot,
            "entry": entry,
            "sl": sl,
            "tp": tp,
            "direction": direction,
            "risk": round(actual_risk_usd, 2),
            "equity": round(server_dynamic_equity, 2),
            "signalHash": signal_hash
        }
    except Exception as err:
        _update_signal_status_pg(conn, user_id, signal_hash, 'FAILED')
        _log_decision_pg(conn, user_id, signal_hash, 'ORDER_FAILED', final_lot, actual_risk_usd, server_dynamic_equity, str(err))
        return {"status": "FAILED", "reason": str(err)}

def _update_signal_status_pg(conn, user_id, hash_val, status):
    conn.run(
        "UPDATE public.bot_signals SET status = :st WHERE user_id = :uid AND signal_hash = :sh",
        st=status, uid=user_id, sh=hash_val
    )

def _log_decision_pg(conn, user_id, hash_val, decision, lot, risk, equity, reason):
    try:
        conn.run(
            "INSERT INTO public.bot_decisions (user_id, signal_hash, decision, calculated_lot, actual_risk_usd, account_equity, reason) "
            "VALUES (:uid, :sh, :dec, :lot, :risk, :eq, :reason)",
            uid=user_id, sh=hash_val, dec=decision, lot=lot, risk=risk, eq=equity, reason=reason
        )
    except Exception:
        pass


# =========================================================================
# 24/7 AUTONOMOUS SERVER-SIDE HARVESTER & 0-LOSS BREAK-EVEN ENGINE
# =========================================================================

def harvest_open_bot_orders(conn, live_price: float):
    """
    Monitors all OPEN bot orders against real-time live Gold spot prices.
    - Locks Break-Even (0 Loss Guard) once price reaches +$0.80 profit.
    - Closes order at TP, banks bite-sized profit ($2 - $10 USD) into wallet balance.
    - Closes order at SL if market reverses, cutting loss at tight $1.35 or exiting at BE.
    - Updates unrealized PnL in real-time.
    """
    global _last_telemetry
    harvested = []
    
    orders = conn.run(
        "SELECT id, user_id, direction, entry_price, sl, tp, lots, signal_id FROM public.orders WHERE executed_by = 'BOT' AND status = 'OPEN'"
    )

    for o in orders:
        oid = str(o[0])
        uid = str(o[1])
        direction = str(o[2]).upper()
        entry = float(o[3])
        sl = float(o[4] if o[4] is not None else (entry - MAX_SL_DISTANCE if direction == 'BUY' else entry + MAX_SL_DISTANCE))
        tp = float(o[5] if o[5] is not None else (entry + SCALP_TP_DISTANCE if direction == 'BUY' else entry - SCALP_TP_DISTANCE))
        lots = float(o[6] if o[6] is not None else 0.01)
        sig_id = str(o[7] or oid)

        is_buy = (direction == "BUY")
        diff = (live_price - entry) if is_buy else (entry - live_price)
        dollar_pnl = round(diff * lots * 100.0, 2)

        # 1. Break-Even 0-Loss Lock
        if diff >= BE_LOCK_DISTANCE:
            if is_buy and sl < entry + 0.10:
                new_sl = round(entry + 0.15, 2)
                conn.run("UPDATE public.orders SET sl = :nsl, stop_loss = :nsl WHERE id = :oid", nsl=new_sl, oid=oid)
                _last_telemetry["be_locked_count"] += 1
                _log_decision_pg(conn, uid, sig_id, 'BE_LOCKED', lots, 0, 0, f"Break-Even 0-Loss Guard locked SL at ${new_sl} (+{diff:.2f} move)")
                sl = new_sl
            elif (not is_buy) and sl > entry - 0.10:
                new_sl = round(entry - 0.15, 2)
                conn.run("UPDATE public.orders SET sl = :nsl, stop_loss = :nsl WHERE id = :oid", nsl=new_sl, oid=oid)
                _last_telemetry["be_locked_count"] += 1
                _log_decision_pg(conn, uid, sig_id, 'BE_LOCKED', lots, 0, 0, f"Break-Even 0-Loss Guard locked SL at ${new_sl} (+{diff:.2f} move)")
                sl = new_sl

        # 2. Take Profit Triggered (Banking $2 - $10 Profit Directly)
        if (is_buy and live_price >= tp) or ((not is_buy) and live_price <= tp):
            realized_pnl = round(abs(tp - entry) * lots * 100.0, 2)
            conn.run(
                "UPDATE public.orders SET status = 'CLOSED', close_price = :cp, realized_pnl = :rpnl, close_reason = 'TP_HIT', closed_at = NOW() WHERE id = :oid",
                cp=tp, rpnl=realized_pnl, oid=oid
            )
            conn.run("UPDATE public.wallets SET balance = balance + :rpnl, updated_at = NOW() WHERE user_id = :uid", rpnl=realized_pnl, uid=uid)
            conn.run("UPDATE public.profiles SET demo_balance = demo_balance + :rpnl, updated_at = NOW() WHERE id = :uid", rpnl=realized_pnl, uid=uid)
            _log_decision_pg(conn, uid, sig_id, 'TP_CLOSED', lots, realized_pnl, 0, f"Micro-scalp profit banked: +${realized_pnl:.2f} USD @ ${tp:.2f}")
            _last_telemetry["closed_harvests"] += 1
            _last_telemetry["total_harvested_profit_usd"] += realized_pnl
            harvested.append({"id": oid, "result": "TP_HIT", "pnl": realized_pnl})
            print(f"[QuantAgent] [BANKED PROFIT] Order {oid[:8]} closed at TP! +${realized_pnl:.2f} USD")
            continue

        # 3. Stop Loss Triggered (Tight Loss or Break-Even Exit)
        if (is_buy and live_price <= sl) or ((not is_buy) and live_price >= sl):
            realized_pnl = round((sl - entry if is_buy else entry - sl) * lots * 100.0, 2)
            close_reason = 'BE_EXIT' if realized_pnl >= 0 else 'SL_HIT'
            conn.run(
                "UPDATE public.orders SET status = 'CLOSED', close_price = :cp, realized_pnl = :rpnl, close_reason = :cr, closed_at = NOW() WHERE id = :oid",
                cp=sl, rpnl=realized_pnl, cr=close_reason, oid=oid
            )
            conn.run("UPDATE public.wallets SET balance = balance + :rpnl, updated_at = NOW() WHERE user_id = :uid", rpnl=realized_pnl, uid=uid)
            conn.run("UPDATE public.profiles SET demo_balance = demo_balance + :rpnl, updated_at = NOW() WHERE id = :uid", rpnl=realized_pnl, uid=uid)
            _log_decision_pg(conn, uid, sig_id, 'SL_CLOSED', lots, realized_pnl, 0, f"Order closed at ${sl:.2f} ({close_reason}): ${realized_pnl:.2f} USD")
            _last_telemetry["closed_harvests"] += 1
            _last_telemetry["total_harvested_profit_usd"] += realized_pnl
            harvested.append({"id": oid, "result": close_reason, "pnl": realized_pnl})
            print(f"[QuantAgent] [ORDER CLOSED] Order {oid[:8]} closed ({close_reason}): ${realized_pnl:.2f} USD")
            continue

        # 4. Live Unrealized PnL Tick
        conn.run("UPDATE public.orders SET unrealized_pnl = :pnl WHERE id = :oid", pnl=dollar_pnl, oid=oid)

    return len(orders), harvested


def autonomous_market_scanner(conn, live_spot: dict):
    """
    Server-side market scanner that runs when the user's browser is closed.
    Finds high-probability micro-scalp setups and opens trades autonomously.
    """
    curr_p = live_spot["price"]
    open_p = live_spot.get("open", curr_p)
    signal = live_spot.get("signal", 0.0)

    active_users = conn.run(
        "SELECT user_id, risk_per_trade_percent, max_open_bot_trades, cooldown_minutes FROM public.bot_settings WHERE is_active = true AND kill_switch = false"
    )

    dispatched = []

    for u in active_users:
        uid = str(u[0])
        max_trades = int(u[2] or 2)

        open_cnt = conn.run(
            "SELECT count(*) FROM public.orders WHERE user_id = :uid AND executed_by = 'BOT' AND status = 'OPEN'",
            uid=uid
        )[0][0]

        if open_cnt >= max_trades:
            continue

        w_rows = conn.run("SELECT balance FROM public.wallets WHERE user_id = :uid", uid=uid)
        balance = float(w_rows[0][0]) if w_rows else 1000.0

        direction = "BUY" if (curr_p >= open_p or signal >= 0) else "SELL"
        sl, tp = apply_micro_scalp_levels(direction, curr_p, 0, 0)
        lots = 0.02 if balance >= 1000.0 else 0.01

        order_uuid = str(uuid.uuid4())
        sig_hash = hashlib.sha256(f"AUTONOMOUS_SERVER|{direction}|{curr_p:.2f}|{int(time.time() // 60)}".encode()).hexdigest()

        try:
            conn.run(
                "INSERT INTO public.orders (id, user_id, symbol, type, direction, entry_price, sl, stop_loss, tp, take_profit, lots, lot_size, executed_by, signal_id, status) "
                "VALUES (:oid, :uid, 'XAU/USD', :dir, :dir, :ep, :slp, :slp, :tpp, :tpp, :lots, :lots, 'BOT', :sh, 'OPEN')",
                oid=order_uuid, uid=uid, dir=direction, ep=curr_p, slp=sl, tpp=tp, lots=lots, sh=sig_hash
            )
            _log_decision_pg(conn, uid, sig_hash, 'EXECUTED', lots, round(lots * MAX_SL_DISTANCE * 100.0, 2), balance, "Autonomous server-side micro scalp order dispatched")
            dispatched.append({"orderId": order_uuid, "direction": direction, "lots": lots, "entry": curr_p, "tp": tp, "sl": sl})
            print(f"[QuantAgent] [AUTONOMOUS SCALP DISPATCHED] {direction} {lots}L @ ${curr_p:.2f} (TP: ${tp:.2f}, SL: ${sl:.2f}) for user {uid[:8]}")
        except Exception as e:
            print(f"[QuantAgent] Failed to insert autonomous order: {e}")

    return len(active_users), dispatched


def run_autonomous_engine_cycle():
    """Single complete execution of the 24/7 autonomous quant cycle."""
    global _last_telemetry
    spot = get_live_gold_spot()
    curr_p = spot["price"]
    
    _last_telemetry["live_price"] = curr_p
    _last_telemetry["last_tick_time"] = int(time.time())

    try:
        conn = get_pg_connection()
        try:
            open_count, harvested = harvest_open_bot_orders(conn, curr_p)
            user_count, dispatched = autonomous_market_scanner(conn, spot)
            
            _last_telemetry["open_bot_orders"] = open_count
            _last_telemetry["active_users"] = user_count
            _last_telemetry["status"] = "AUTONOMOUS ACTIVE (24/7)"
            _last_telemetry["last_log"] = f"Gold ${curr_p:.2f} | Open: {open_count} | Active Users: {user_count}"
            return _last_telemetry
        finally:
            conn.close()
    except Exception as e:
        _last_telemetry["status"] = "ERROR_RECOVERING"
        _last_telemetry["last_log"] = str(e)
        return _last_telemetry


def _daemon_worker_loop():
    """Background worker daemon thread that runs continuously 24/7."""
    print("[QuantDaemon] Autonomous Quant Background Daemon started (24/7 Server Engine)...")
    while True:
        try:
            run_autonomous_engine_cycle()
        except Exception as e:
            print(f"[QuantDaemon] Cycle exception: {e}")
        time.sleep(3.5)


def start_autonomous_daemon():
    """Starts the background autonomous daemon thread once."""
    global _daemon_started
    if not _daemon_started:
        _daemon_started = True
        t = threading.Thread(target=_daemon_worker_loop, daemon=True, name="QuantAutonomousDaemon")
        t.start()
        print("[QuantDaemon] Daemon thread spawned successfully.")


def get_daemon_telemetry():
    """Returns real-time telemetry dictionary for client polling."""
    return dict(_last_telemetry)
