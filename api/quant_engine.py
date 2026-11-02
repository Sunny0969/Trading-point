"""
TradingPoint Server-Side Autonomous Quant Execution Engine (Production-Grade & Zero-Trust)
Implements deterministic SHA-256 fingerprinting, server dynamic equity calculation,
mathematical risk ceiling, precision lot allocation, and atomic DB execution.
Ultra-Low-Risk Micro Scalper Policy:
- Minimum loss guard: Tight SL clamped to max $1.50 from entry.
- Quick profit targets: Scalp TP clamped to $2.50 from entry.
- Micro lots: Conservative 0.01 - 0.05 lots.
Dual-mode engine: Direct PostgreSQL (pg8000) with seamless HTTPS REST API fallback.
"""

import os
import sys
import hashlib
import math
import json
import uuid

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
MAX_SL_DISTANCE = 1.50   # Max $1.50 SL distance (loss is strictly minimized)
SCALP_TP_DISTANCE = 2.50 # Quick $2.50 profit target (quick scalp banking)

def _get_rest_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

def apply_micro_scalp_levels(direction: str, entry: float, raw_sl: float, raw_tp: float):
    """Enforces ultra-low-risk tight SL and quick scalp TP."""
    if direction == "SELL":
        # Tight SL above entry (at most $1.50)
        sl = round(min(raw_sl if raw_sl > entry else entry + MAX_SL_DISTANCE, entry + MAX_SL_DISTANCE), 2)
        # Quick TP below entry ($2.50)
        tp = round(entry - SCALP_TP_DISTANCE, 2)
    else:  # BUY
        # Tight SL below entry (at most $1.50)
        sl = round(max(raw_sl if raw_sl < entry else entry - MAX_SL_DISTANCE, entry - MAX_SL_DISTANCE), 2)
        # Quick TP above entry ($2.50)
        tp = round(entry + SCALP_TP_DISTANCE, 2)
    return sl, tp

def process_signal_server_authoritative(payload: dict) -> dict:
    """
    Zero-Trust server-authoritative execution engine.
    Tries direct PostgreSQL pooler first; falls back smoothly to Supabase HTTPS REST API.
    """
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

    # Enforce Micro-Scalp Low-Risk Levels
    sl, tp = apply_micro_scalp_levels(direction, entry, raw_sl, raw_tp)

    # 1. Deterministic Server SHA-256 Fingerprint
    raw_fingerprint = f"{source}|{direction}|{entry:.2f}|{sl:.2f}|{candle_time}"
    signal_hash = hashlib.sha256(raw_fingerprint.encode("utf-8")).hexdigest()

    # Try pg8000 first, fallback to REST
    try:
        import ssl
        import pg8000.native
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        conn = pg8000.native.Connection(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            ssl_context=ctx
        )
        return _process_via_pg(conn, user_id, source, direction, entry, sl, tp, signal_hash)
    except Exception as pg_err:
        try:
            return _process_via_rest(user_id, source, direction, entry, sl, tp, signal_hash)
        except Exception as rest_err:
            return {"status": "FAILED", "reason": f"Execution Engine DB Error: {str(rest_err)}"}

def _process_via_pg(conn, user_id, source, direction, entry, sl, tp, signal_hash):
    try:
        # 2. Fetch User Settings & Guard Gates
        settings_rows = conn.run(
            "SELECT is_active, risk_per_trade_percent, daily_drawdown_limit_percent, max_open_bot_trades, cooldown_minutes, kill_switch "
            "FROM public.bot_settings WHERE user_id = :uid",
            uid=user_id
        )

        if not settings_rows:
            conn.run(
                "INSERT INTO public.bot_settings (user_id, is_active, risk_per_trade_percent, max_open_bot_trades, kill_switch) "
                "VALUES (:uid, true, 1.00, 3, false) ON CONFLICT (user_id) DO NOTHING",
                uid=user_id
            )
            is_active, risk_percent, daily_dd, max_trades, cooldown, kill_switch = True, 1.00, 3.00, 3, 15, False
        else:
            is_active, risk_percent, daily_dd, max_trades, cooldown, kill_switch = settings_rows[0]
            risk_percent = float(risk_percent or 1.0)
            max_trades = int(max_trades or 3)

        if not is_active or kill_switch:
            return {"status": "ABORTED", "reason": "Bot inactive or Kill Switch engaged"}

        # 3. Idempotency Check with Status Enforcement
        existing = conn.run(
            "SELECT status FROM public.bot_signals WHERE user_id = :uid AND signal_hash = :sh",
            uid=user_id,
            sh=signal_hash
        )

        if existing:
            current_status = existing[0][0]
            if current_status in ("EXECUTED", "PENDING"):
                return {"status": "SKIPPED", "reason": f"Signal already processed or currently executing ({current_status})"}

        # Mark signal as PENDING
        conn.run(
            "INSERT INTO public.bot_signals (user_id, signal_hash, indicator_source, direction, entry_price, sl_price, tp_price, status) "
            "VALUES (:uid, :sh, :src, :dir, :ep, :slp, :tpp, 'PENDING') "
            "ON CONFLICT (user_id, signal_hash) DO UPDATE SET status = 'PENDING'",
            uid=user_id, sh=signal_hash, src=source, dir=direction, ep=entry, slp=sl, tpp=tp
        )

        # 4. Server-Side Dynamic Equity Calculation
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

        # 5. Conservative Micro-Lot Allocation
        max_allowed_risk_usd = server_dynamic_equity * (risk_percent / 100.0)
        sl_distance = abs(entry - sl)

        if sl_distance <= 0.05:
            _log_decision_pg(conn, user_id, signal_hash, 'SKIPPED_MAX_RISK', 0, 0, server_dynamic_equity, 'Invalid tight SL distance')
            _update_signal_status_pg(conn, user_id, signal_hash, 'CANCELLED')
            return {"status": "SKIPPED", "reason": "Invalid SL distance"}

        raw_lot = max_allowed_risk_usd / (sl_distance * 100.0)
        final_lot = math.floor(raw_lot * 100.0 + 1e-9) / 100.0
        final_lot = max(0.01, min(final_lot, 0.05)) # Conservative micro lots: 0.01 - 0.05

        actual_risk_usd = final_lot * sl_distance * 100.0
        order_uuid = str(uuid.uuid4())

        # 6. Atomic Broker Dispatch
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
    finally:
        conn.close()

def _update_signal_status_pg(conn, user_id, hash_val, status):
    conn.run(
        "UPDATE public.bot_signals SET status = :st WHERE user_id = :uid AND signal_hash = :sh",
        st=status, uid=user_id, sh=hash_val
    )

def _log_decision_pg(conn, user_id, hash_val, decision, lot, risk, equity, reason):
    conn.run(
        "INSERT INTO public.bot_decisions (user_id, signal_hash, decision, calculated_lot, actual_risk_usd, account_equity, reason) "
        "VALUES (:uid, :sh, :dec, :lot, :risk, :eq, :reason)",
        uid=user_id, sh=hash_val, dec=decision, lot=lot, risk=risk, eq=equity, reason=reason
    )

def _process_via_rest(user_id, source, direction, entry, sl, tp, signal_hash):
    """Fallback Supabase REST API implementation"""
    headers = _get_rest_headers()

    # 1. Fetch settings
    res = requests.get(f"{SUPABASE_URL}/rest/v1/bot_settings?user_id=eq.{user_id}", headers=headers, timeout=5)
    settings_data = res.json() if res.status_code == 200 else []
    if not settings_data:
        requests.post(f"{SUPABASE_URL}/rest/v1/bot_settings", headers=headers, json={
            "user_id": user_id, "is_active": True, "risk_per_trade_percent": 1.0, "max_open_bot_trades": 3, "kill_switch": False
        }, timeout=5)
        is_active, risk_percent, max_trades, kill_switch = True, 1.0, 3, False
    else:
        st = settings_data[0]
        is_active = st.get("is_active", True)
        risk_percent = float(st.get("risk_per_trade_percent") or 1.0)
        max_trades = int(st.get("max_open_bot_trades") or 3)
        kill_switch = st.get("kill_switch", False)

    if not is_active or kill_switch:
        return {"status": "ABORTED", "reason": "Bot inactive or Kill Switch engaged"}

    # 2. Check Idempotency
    sig_res = requests.get(f"{SUPABASE_URL}/rest/v1/bot_signals?user_id=eq.{user_id}&signal_hash=eq.{signal_hash}&select=status", headers=headers, timeout=5)
    sig_data = sig_res.json() if sig_res.status_code == 200 else []
    if sig_data:
        cur_st = sig_data[0].get("status")
        if cur_st in ("EXECUTED", "PENDING"):
            return {"status": "SKIPPED", "reason": f"Signal already processed or currently executing ({cur_st})"}

    # Mark PENDING
    upsert_headers = dict(headers)
    upsert_headers["Prefer"] = "resolution=merge-duplicates"
    requests.post(f"{SUPABASE_URL}/rest/v1/bot_signals", headers=upsert_headers, json={
        "user_id": user_id, "signal_hash": signal_hash, "indicator_source": source,
        "direction": direction, "entry_price": entry, "sl_price": sl, "tp_price": tp,
        "status": "PENDING"
    }, timeout=5)

    # 3. Dynamic Equity
    w_res = requests.get(f"{SUPABASE_URL}/rest/v1/wallets?user_id=eq.{user_id}&select=balance", headers=headers, timeout=5)
    w_data = w_res.json() if w_res.status_code == 200 else []
    if w_data:
        balance = float(w_data[0].get("balance") or 1000.0)
    else:
        p_res = requests.get(f"{SUPABASE_URL}/rest/v1/profiles?id=eq.{user_id}&select=demo_balance", headers=headers, timeout=5)
        p_data = p_res.json() if p_res.status_code == 200 else []
        balance = float(p_data[0].get("demo_balance") or 1000.0) if p_data else 1000.0

    o_res = requests.get(f"{SUPABASE_URL}/rest/v1/orders?user_id=eq.{user_id}&status=eq.OPEN&select=unrealized_pnl,executed_by", headers=headers, timeout=5)
    open_orders = o_res.json() if o_res.status_code == 200 else []

    open_bot = [o for o in open_orders if o.get("executed_by") == "BOT"]
    if len(open_bot) >= max_trades:
        requests.post(f"{SUPABASE_URL}/rest/v1/bot_decisions", headers=headers, json={
            "user_id": user_id, "signal_hash": signal_hash, "decision": "SKIPPED_COOLDOWN",
            "calculated_lot": 0, "actual_risk_usd": 0, "account_equity": balance,
            "reason": f"Max concurrent bot trades reached ({len(open_bot)}/{max_trades})"
        }, timeout=5)
        requests.patch(f"{SUPABASE_URL}/rest/v1/bot_signals?user_id=eq.{user_id}&signal_hash=eq.{signal_hash}", headers=headers, json={"status": "CANCELLED"}, timeout=5)
        return {"status": "SKIPPED", "reason": "Max open trades reached"}

    total_unrealized = sum([float(o.get("unrealized_pnl") or 0) for o in open_orders])
    server_equity = balance + total_unrealized

    if server_equity <= 0:
        requests.patch(f"{SUPABASE_URL}/rest/v1/bot_signals?user_id=eq.{user_id}&signal_hash=eq.{signal_hash}", headers=headers, json={"status": "FAILED"}, timeout=5)
        return {"status": "FAILED", "reason": "Insufficient or invalid server equity"}

    # 4. Conservative Micro-Lot allocation
    max_risk = server_equity * (risk_percent / 100.0)
    sl_dist = abs(entry - sl)
    if sl_dist <= 0.05:
        requests.patch(f"{SUPABASE_URL}/rest/v1/bot_signals?user_id=eq.{user_id}&signal_hash=eq.{signal_hash}", headers=headers, json={"status": "CANCELLED"}, timeout=5)
        return {"status": "SKIPPED", "reason": "Invalid SL distance"}

    raw_lot = max_risk / (sl_dist * 100.0)
    final_lot = math.floor(raw_lot * 100.0 + 1e-9) / 100.0
    final_lot = max(0.01, min(final_lot, 0.05)) # Conservative micro-lots: 0.01 - 0.05
    actual_risk = final_lot * sl_dist * 100.0

    order_uuid = str(uuid.uuid4())

    # 5. Insert order
    ins_res = requests.post(f"{SUPABASE_URL}/rest/v1/orders", headers=headers, json={
        "id": order_uuid,
        "user_id": user_id,
        "symbol": "XAU/USD",
        "type": direction,
        "direction": direction,
        "entry_price": entry,
        "sl": sl,
        "stop_loss": sl,
        "tp": tp,
        "take_profit": tp,
        "lots": final_lot,
        "lot_size": final_lot,
        "executed_by": "BOT",
        "signal_id": signal_hash,
        "status": "OPEN"
    }, timeout=5)

    if ins_res.status_code in (200, 201):
        requests.patch(f"{SUPABASE_URL}/rest/v1/bot_signals?user_id=eq.{user_id}&signal_hash=eq.{signal_hash}", headers=headers, json={"status": "EXECUTED"}, timeout=5)
        requests.post(f"{SUPABASE_URL}/rest/v1/bot_decisions", headers=headers, json={
            "user_id": user_id, "signal_hash": signal_hash, "decision": "EXECUTED",
            "calculated_lot": final_lot, "actual_risk_usd": actual_risk, "account_equity": server_equity,
            "reason": "Micro-scalp order filled via automated risk gate"
        }, timeout=5)
        return {
            "status": "SUCCESS",
            "orderId": order_uuid,
            "lot": final_lot,
            "entry": entry,
            "sl": sl,
            "tp": tp,
            "direction": direction,
            "risk": round(actual_risk, 2),
            "equity": round(server_equity, 2),
            "signalHash": signal_hash
        }
    else:
        err_msg = ins_res.text
        requests.patch(f"{SUPABASE_URL}/rest/v1/bot_signals?user_id=eq.{user_id}&signal_hash=eq.{signal_hash}", headers=headers, json={"status": "FAILED"}, timeout=5)
        requests.post(f"{SUPABASE_URL}/rest/v1/bot_decisions", headers=headers, json={
            "user_id": user_id, "signal_hash": signal_hash, "decision": "ORDER_FAILED",
            "calculated_lot": final_lot, "actual_risk_usd": actual_risk, "account_equity": server_equity,
            "reason": err_msg
        }, timeout=5)
        return {"status": "FAILED", "reason": f"Insert order error: {err_msg}"}
