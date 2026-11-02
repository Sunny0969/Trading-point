import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";
import { createHash } from "https://deno.land/std@0.177.0/node/crypto.ts";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

interface SignalPayload {
  userId: string;
  source: string;
  direction: "BUY" | "SELL";
  entry: number;
  sl: number;
  tp: number;
  candleTime: string | number;
}

// User directive: "mujhe heavy profit nhn chaiye, bot chote chote profit le, loss minimum ho bilkul na hone ke barabar, long stop loss na le"
const MAX_SL_DISTANCE = 1.50;   // Max $1.50 SL distance
const SCALP_TP_DISTANCE = 2.50; // Quick $2.50 scalp profit target

export async function processSignalServerAuthoritative(supabase: any, payload: SignalPayload) {
  const { userId, source, direction, entry, candleTime } = payload;
  let raw_sl = Number(payload.sl);
  let raw_tp = Number(payload.tp);

  // Micro-Scalp Low-Risk Clamp
  let sl = raw_sl;
  let tp = raw_tp;
  if (direction === "SELL") {
    sl = Number((Math.min(raw_sl > entry ? raw_sl : entry + MAX_SL_DISTANCE, entry + MAX_SL_DISTANCE)).toFixed(2));
    tp = Number((entry - SCALP_TP_DISTANCE).toFixed(2));
  } else {
    sl = Number((Math.max(raw_sl < entry ? raw_sl : entry - MAX_SL_DISTANCE, entry - MAX_SL_DISTANCE)).toFixed(2));
    tp = Number((entry + SCALP_TP_DISTANCE).toFixed(2));
  }

  // 1. Deterministic Server SHA-256 Fingerprint
  const rawFingerprint = `${source}|${direction}|${Number(entry).toFixed(2)}|${sl.toFixed(2)}|${candleTime}`;
  const signalHash = createHash("sha256").update(rawFingerprint).digest("hex");

  // 2. Fetch User Settings & Guard Gates
  const { data: settings } = await supabase
    .from("bot_settings")
    .select("*")
    .eq("user_id", userId)
    .single();

  if (!settings || !settings.is_active || settings.kill_switch) {
    return { status: "ABORTED", reason: "Bot inactive or Kill Switch engaged" };
  }

  // 3. Idempotency Check with Status Enforcement
  const { data: existingSignal } = await supabase
    .from("bot_signals")
    .select("status")
    .eq("user_id", userId)
    .eq("signal_hash", signalHash)
    .maybeSingle();

  if (existingSignal && (existingSignal.status === "EXECUTED" || existingSignal.status === "PENDING")) {
    return { status: "SKIPPED", reason: "Signal already processed or currently executing" };
  }

  // Mark signal as PENDING
  await supabase.from("bot_signals").upsert({
    user_id: userId,
    signal_hash: signalHash,
    indicator_source: source,
    direction: direction,
    entry_price: entry,
    sl_price: sl,
    tp_price: tp,
    status: "PENDING"
  });

  // 4. Server-Side Dynamic Equity Calculation
  const { data: wallet } = await supabase
    .from("wallets")
    .select("balance")
    .eq("user_id", userId)
    .single();

  const walletBalance = wallet ? parseFloat(wallet.balance) : 1000.0;

  const { data: openOrders } = await supabase
    .from("orders")
    .select("unrealized_pnl, executed_by")
    .eq("user_id", userId)
    .eq("status", "OPEN");

  const openBotOrders = (openOrders || []).filter((o: any) => o.executed_by === "BOT");
  if (openBotOrders.length >= (settings.max_open_bot_trades || 3)) {
    await logDecision(supabase, userId, signalHash, "SKIPPED_COOLDOWN", 0, 0, 0, "Max concurrent bot trades reached");
    await updateSignalStatus(supabase, userId, signalHash, "CANCELLED");
    return { status: "SKIPPED", reason: "Max open trades reached" };
  }

  const totalUnrealizedPnL = (openOrders || []).reduce((acc: number, o: any) => acc + (parseFloat(o.unrealized_pnl) || 0), 0);
  const serverDynamicEquity = walletBalance + totalUnrealizedPnL;

  if (serverDynamicEquity <= 0) {
    await updateSignalStatus(supabase, userId, signalHash, "FAILED");
    return { status: "FAILED", reason: "Insufficient or invalid server equity" };
  }

  // 5. Conservative Micro-Lot Allocation
  const maxAllowedRiskUsd = serverDynamicEquity * ((settings.risk_per_trade_percent || 1.0) / 100);
  const slDistance = Math.abs(entry - sl);
  
  if (slDistance <= 0.05) {
    await logDecision(supabase, userId, signalHash, "SKIPPED_MAX_RISK", 0, 0, serverDynamicEquity, "Invalid tight SL distance");
    await updateSignalStatus(supabase, userId, signalHash, "CANCELLED");
    return { status: "SKIPPED", reason: "Invalid SL distance" };
  }

  const rawLot = maxAllowedRiskUsd / (slDistance * 100);
  let finalLot = Math.floor(rawLot * 100 + 1e-9) / 100;
  finalLot = Math.max(0.01, Math.min(finalLot, 0.05)); // Conservative micro lots

  const actualRiskUsd = finalLot * slDistance * 100;
  const orderId = crypto.randomUUID();

  // 6. Atomic Broker Dispatch
  try {
    const { error: orderError } = await supabase.from("orders").insert({
      id: orderId,
      user_id: userId,
      symbol: "XAU/USD",
      type: direction,
      direction: direction,
      entry_price: entry,
      sl: sl,
      stop_loss: sl,
      tp: tp,
      take_profit: tp,
      lots: finalLot,
      lot_size: finalLot,
      executed_by: "BOT",
      signal_id: signalHash,
      status: "OPEN"
    });

    if (orderError) throw orderError;

    await updateSignalStatus(supabase, userId, signalHash, "EXECUTED");
    await logDecision(supabase, userId, signalHash, "EXECUTED", finalLot, actualRiskUsd, serverDynamicEquity, "Micro-scalp order filled via automated risk gate");

    return {
      status: "SUCCESS",
      orderId: orderId,
      lot: finalLot,
      entry: entry,
      sl: sl,
      tp: tp,
      direction: direction,
      risk: Number(actualRiskUsd.toFixed(2)),
      equity: Number(serverDynamicEquity.toFixed(2))
    };
  } catch (err: any) {
    await updateSignalStatus(supabase, userId, signalHash, "FAILED");
    await logDecision(supabase, userId, signalHash, "ORDER_FAILED", finalLot, actualRiskUsd, serverDynamicEquity, err.message);
    return { status: "FAILED", reason: err.message };
  }
}

async function updateSignalStatus(supabase: any, userId: string, hash: string, status: string) {
  await supabase.from("bot_signals").update({ status }).match({ user_id: userId, signal_hash: hash });
}

async function logDecision(supabase: any, userId: string, hash: string, decision: string, lot: number, risk: number, equity: number, reason: string) {
  await supabase.from("bot_decisions").insert({
    user_id: userId,
    signal_hash: hash,
    decision,
    calculated_lot: lot,
    actual_risk_usd: risk,
    account_equity: equity,
    reason
  });
}

// HTTP Server Endpoint for Supabase Edge Functions
serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  try {
    const supabaseUrl = Deno.env.get("SUPABASE_URL") ?? "";
    const supabaseServiceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "";
    const supabase = createClient(supabaseUrl, supabaseServiceKey);

    const payload = await req.json();
    const result = await processSignalServerAuthoritative(supabase, payload);

    return new Response(JSON.stringify(result), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
      status: 200,
    });
  } catch (error: any) {
    return new Response(JSON.stringify({ error: error.message }), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
      status: 400,
    });
  }
});
