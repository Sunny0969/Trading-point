-- ========================================================
-- PRODUCTION MIGRATION: Server-Side Autonomous Quant Execution Engine
-- Idempotent, Multi-Tenant Row Level Security (RLS), Composite Keys
-- ========================================================

-- 1. Orders Table Additive Columns
ALTER TABLE public.orders 
ADD COLUMN IF NOT EXISTS executed_by TEXT DEFAULT 'MANUAL',
ADD COLUMN IF NOT EXISTS signal_id TEXT,
ADD COLUMN IF NOT EXISTS direction TEXT,
ADD COLUMN IF NOT EXISTS stop_loss NUMERIC(15, 3),
ADD COLUMN IF NOT EXISTS take_profit NUMERIC(15, 3),
ADD COLUMN IF NOT EXISTS lot_size NUMERIC(10, 2),
ADD COLUMN IF NOT EXISTS unrealized_pnl NUMERIC(15, 2) DEFAULT 0.00;

-- 2. Bot Settings Table (Per-user configuration)
CREATE TABLE IF NOT EXISTS public.bot_settings (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    is_active BOOLEAN DEFAULT false,
    risk_per_trade_percent NUMERIC(4,2) DEFAULT 1.00,
    daily_drawdown_limit_percent NUMERIC(4,2) DEFAULT 3.00,
    max_open_bot_trades INT DEFAULT 2,
    cooldown_minutes INT DEFAULT 15,
    min_confluence_score NUMERIC(4,2) DEFAULT 80.00,
    kill_switch BOOLEAN DEFAULT false,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.bot_settings ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own bot settings" ON public.bot_settings;
CREATE POLICY "Users can view own bot settings" 
ON public.bot_settings FOR SELECT 
USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own bot settings" ON public.bot_settings;
CREATE POLICY "Users can update own bot settings" 
ON public.bot_settings FOR UPDATE 
USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own bot settings" ON public.bot_settings;
CREATE POLICY "Users can insert own bot settings" 
ON public.bot_settings FOR INSERT 
WITH CHECK (auth.uid() = user_id);

-- 3. Bot Signals Table (Composite Key for Multi-Tenant Safety & Execution State)
CREATE TABLE IF NOT EXISTS public.bot_signals (
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    signal_hash TEXT NOT NULL,
    indicator_source TEXT NOT NULL,
    direction TEXT NOT NULL,
    entry_price NUMERIC(10,2) NOT NULL,
    sl_price NUMERIC(10,2) NOT NULL,
    tp_price NUMERIC(10,2) NOT NULL,
    status TEXT DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'EXECUTED', 'FAILED', 'CANCELLED')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (user_id, signal_hash)
);

ALTER TABLE public.bot_signals ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own signals" ON public.bot_signals;
CREATE POLICY "Users can view own signals" 
ON public.bot_signals FOR SELECT 
USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Service role can manage all signals" ON public.bot_signals;
CREATE POLICY "Service role can manage all signals" 
ON public.bot_signals FOR ALL 
USING (auth.jwt() ->> 'role' = 'service_role');

-- 4. Audit & Decision Telemetry Log (Why an order was taken or skipped)
CREATE TABLE IF NOT EXISTS public.bot_decisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    signal_hash TEXT NOT NULL,
    decision TEXT NOT NULL CHECK (decision IN ('EXECUTED', 'SKIPPED_MAX_RISK', 'SKIPPED_DAILY_LIMIT', 'SKIPPED_COOLDOWN', 'SKIPPED_KILL_SWITCH', 'ORDER_FAILED')),
    calculated_lot NUMERIC(6,2),
    actual_risk_usd NUMERIC(10,2),
    account_equity NUMERIC(12,2),
    reason TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.bot_decisions ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own decisions" ON public.bot_decisions;
CREATE POLICY "Users can view own decisions" 
ON public.bot_decisions FOR SELECT 
USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Service role can insert decisions" ON public.bot_decisions;
CREATE POLICY "Service role can insert decisions" 
ON public.bot_decisions FOR INSERT 
WITH CHECK (auth.jwt() ->> 'role' = 'service_role');

-- 5. Wallets Compatibility Table (Guarantees balance availability & sync with profiles)
CREATE TABLE IF NOT EXISTS public.wallets (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    balance NUMERIC(15, 2) NOT NULL DEFAULT 1000.00,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.wallets ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own wallet" ON public.wallets;
CREATE POLICY "Users can view own wallet" ON public.wallets FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own wallet" ON public.wallets;
CREATE POLICY "Users can update own wallet" ON public.wallets FOR UPDATE USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own wallet" ON public.wallets;
CREATE POLICY "Users can insert own wallet" ON public.wallets FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Auto sync existing profiles into wallets
INSERT INTO public.wallets (user_id, balance)
SELECT id, demo_balance FROM public.profiles
ON CONFLICT (user_id) DO UPDATE SET balance = EXCLUDED.balance;

-- Permissions
GRANT ALL ON public.bot_settings TO anon, authenticated, service_role;
GRANT ALL ON public.bot_signals TO anon, authenticated, service_role;
GRANT ALL ON public.bot_decisions TO anon, authenticated, service_role;
GRANT ALL ON public.wallets TO anon, authenticated, service_role;
