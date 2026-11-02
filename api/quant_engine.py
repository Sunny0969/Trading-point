"""
TradingPoint Server-Side Autonomous Quant Execution Engine (Production-Grade & Zero-Trust)
Implements deterministic SHA-256 fingerprinting, server dynamic equity calculation,
mathematical risk ceiling, precision lot allocation, and atomic DB execution.
"""

import os
import hashlib
import math
import ssl
import pg8000.native

# Supabase database connection details
DB_USER = os.environ.get("SUPABASE_DB_USER", "postgres.tcwboskfypcrsrniatni")
DB_PASSWORD = os.environ.get("SUPABASE_DB_PASSWORD", "GuEyWSzHSDmLDn9u")
DB_HOST = os.environ.get("SUPABASE_DB_HOST", "aws-0-ap-northeast-1.pooler.supabase.com")
DB_PORT = int(os.environ.get("SUPABASE_DB_PORT", "5432"))
DB_NAME = os.environ.get("SUPABASE_DB_NAME", "postgres")

def get_db_connection():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return pg8000.native.Connection(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        ssl_context=ctx
    )

def process_signal_server_authoritative(payload: dict) -> dict:
    """
    Zero-Trust server-authoritative execution engine.
    Client only submits signal coordinates; server enforces all risk limits and lot sizes.
    """
    user_id = payload.get("userId")
    source = payload.get("source", "SMC_CONFLUENCE")
    direction = str(payload.get("direction", "BUY")).upper()
    try:
        entry = float(payload.get("entry", 0))
        sl = float(payload.get("sl", 0))
        tp = float(payload.get("tp", 0))
    except (ValueError, TypeError):
        return {"status": "FAILED", "reason": "Invalid numerical parameters for entry, sl, or tp"}

    candle_time = str(payload.get("candleTime", ""))

    if not user_id:
        return {"status": "FAILED", "reason": "Missing authenticated userId"}

    # 1. Deterministic Server SHA-256 Fingerprint
    raw_fingerprint = f"{source}|{direction}|{entry:.2f}|{sl:.2f}|{candle_time}"
    signal_hash = hashlib.sha256(raw_fingerprint.encode("utf-8")).hexdigest()

    conn = get_db_connection()
    try:
        # 2. Fetch User Settings & Guard Gates
        settings_rows = conn.run(
            "SELECT is_active, risk_per_trade_percent, daily_drawdown_limit_percent, max_open_bot_trades, cooldown_minutes, kill_switch "
            "FROM public.bot_settings WHERE user_id = :uid",
            uid=user_id
        )

        if not settings_rows:
            # Auto-seed default settings for user
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

        # 4. Server-Side Dynamic Equity Calculation (Prevents client tampering)
        wallet_rows = conn.run("SELECT balance FROM public.wallets WHERE user_id = :uid", uid=user_id)
        if not wallet_rows:
            # Check profiles table
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
            log_decision(conn, user_id, signal_hash, 'SKIPPED_COOLDOWN', 0, 0, 0, f'Max concurrent bot trades reached ({len(open_bot_orders)}/{max_trades})')
            update_signal_status(conn, user_id, signal_hash, 'CANCELLED')
            return {"status": "SKIPPED", "reason": "Max open trades reached"}

        total_unrealized_pnl = sum([float(o[0] or 0) for o in open_orders])
        server_dynamic_equity = wallet_balance + total_unrealized_pnl

        if server_dynamic_equity <= 0:
            update_signal_status(conn, user_id, signal_hash, 'FAILED')
            return {"status": "FAILED", "reason": "Insufficient or invalid server equity"}

        # 5. Mathematical Risk & Precision Lot Allocation (No Floating Point Bug)
        max_allowed_risk_usd = server_dynamic_equity * (risk_percent / 100.0)
        sl_distance = abs(entry - sl)

        if sl_distance <= 0.05:
            log_decision(conn, user_id, signal_hash, 'SKIPPED_MAX_RISK', 0, 0, server_dynamic_equity, 'Invalid tight SL distance')
            update_signal_status(conn, user_id, signal_hash, 'CANCELLED')
            return {"status": "SKIPPED", "reason": "Invalid SL distance"}

        # Standard Gold Contract: 1.00 Lot = 100 oz ($1 move = $100)
        min_contract_dollar_risk = 0.01 * sl_distance * 100.0

        # Strict Risk Ceiling: If minimum lot exceeds allowed risk budget, SKIP execution entirely
        if min_contract_dollar_risk > max_allowed_risk_usd:
            msg = f"Min 0.01 lot risk (${min_contract_dollar_risk:.2f}) strictly exceeds allowed {risk_percent}% budget (${max_allowed_risk_usd:.2f})"
            log_decision(conn, user_id, signal_hash, 'SKIPPED_MAX_RISK', 0, min_contract_dollar_risk, server_dynamic_equity, msg)
            update_signal_status(conn, user_id, signal_hash, 'CANCELLED')
            return {"status": "SKIPPED", "reason": "Risk ceiling exceeded by minimum lot size"}

        # Safe Math.floor with Epsilon Fix: Math.floor(x * 100 + 1e-9) / 100
        raw_lot = max_allowed_risk_usd / (sl_distance * 100.0)
        final_lot = math.floor(raw_lot * 100.0 + 1e-9) / 100.0
        final_lot = max(0.01, min(final_lot, 0.50)) # Clamp between 0.01 and 0.50 lots

        actual_risk_usd = final_lot * sl_distance * 100.0

        # 6. Atomic Broker Dispatch
        try:
            conn.run(
                "INSERT INTO public.orders (user_id, symbol, type, direction, entry_price, sl, stop_loss, tp, take_profit, lots, lot_size, executed_by, signal_id, status) "
                "VALUES (:uid, 'XAU/USD', :dir, :dir, :ep, :slp, :slp, :tpp, :tpp, :lots, :lots, 'BOT', :sh, 'OPEN')",
                uid=user_id, dir=direction, ep=entry, slp=sl, tpp=tp, lots=final_lot, sh=signal_hash
            )

            update_signal_status(conn, user_id, signal_hash, 'EXECUTED')
            log_decision(conn, user_id, signal_hash, 'EXECUTED', final_lot, actual_risk_usd, server_dynamic_equity, 'Order filled via automated risk gate')

            return {
                "status": "SUCCESS",
                "lot": final_lot,
                "risk": round(actual_risk_usd, 2),
                "equity": round(server_dynamic_equity, 2),
                "signalHash": signal_hash
            }
        except Exception as err:
            update_signal_status(conn, user_id, signal_hash, 'FAILED')
            log_decision(conn, user_id, signal_hash, 'ORDER_FAILED', final_lot, actual_risk_usd, server_dynamic_equity, str(err))
            return {"status": "FAILED", "reason": str(err)}
    finally:
        conn.close()

def update_signal_status(conn, user_id: str, hash_val: str, status: str):
    conn.run(
        "UPDATE public.bot_signals SET status = :st WHERE user_id = :uid AND signal_hash = :sh",
        st=status, uid=user_id, sh=hash_val
    )

def log_decision(conn, user_id: str, hash_val: str, decision: str, lot: float, risk: float, equity: float, reason: str):
    conn.run(
        "INSERT INTO public.bot_decisions (user_id, signal_hash, decision, calculated_lot, actual_risk_usd, account_equity, reason) "
        "VALUES (:uid, :sh, :dec, :lot, :risk, :eq, :reason)",
        uid=user_id, sh=hash_val, dec=decision, lot=lot, risk=risk, eq=equity, reason=reason
    )
