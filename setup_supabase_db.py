import ssl
import pg8000.native

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

conn = pg8000.native.Connection(
    user='postgres.tcwboskfypcrsrniatni',
    password='GuEyWSzHSDmLDn9u',
    host='aws-0-ap-northeast-1.pooler.supabase.com',
    port=5432,
    database='postgres',
    ssl_context=ctx
)

sql_statements = [
    """
    CREATE TABLE IF NOT EXISTS public.profiles (
        id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
        email TEXT,
        demo_balance NUMERIC(15, 2) NOT NULL DEFAULT 1000.00,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS public.orders (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
        symbol TEXT NOT NULL DEFAULT 'XAU/USD',
        type TEXT NOT NULL CHECK (type IN ('BUY', 'SELL')),
        lots NUMERIC(10, 2) NOT NULL CHECK (lots >= 0.01),
        entry_price NUMERIC(15, 3) NOT NULL,
        margin NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
        sl NUMERIC(15, 3),
        tp NUMERIC(15, 3),
        status TEXT NOT NULL DEFAULT 'OPEN' CHECK (status IN ('OPEN', 'CLOSED', 'CANCELLED')),
        close_price NUMERIC(15, 3),
        realized_pnl NUMERIC(15, 2),
        close_reason TEXT,
        opened_at TIMESTAMPTZ DEFAULT NOW(),
        closed_at TIMESTAMPTZ
    );
    """,
    """
    -- Enable Row Level Security
    ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
    ALTER TABLE public.orders ENABLE ROW LEVEL SECURITY;
    """,
    """
    -- Profiles Policies
    DROP POLICY IF EXISTS "Users can view own profile" ON public.profiles;
    CREATE POLICY "Users can view own profile" ON public.profiles FOR SELECT USING (auth.uid() = id);

    DROP POLICY IF EXISTS "Users can update own profile" ON public.profiles;
    CREATE POLICY "Users can update own profile" ON public.profiles FOR UPDATE USING (auth.uid() = id);

    DROP POLICY IF EXISTS "Users can insert own profile" ON public.profiles;
    CREATE POLICY "Users can insert own profile" ON public.profiles FOR INSERT WITH CHECK (auth.uid() = id);
    """,
    """
    -- Orders Policies
    DROP POLICY IF EXISTS "Users can view own orders" ON public.orders;
    CREATE POLICY "Users can view own orders" ON public.orders FOR SELECT USING (auth.uid() = user_id);

    DROP POLICY IF EXISTS "Users can insert own orders" ON public.orders;
    CREATE POLICY "Users can insert own orders" ON public.orders FOR INSERT WITH CHECK (auth.uid() = user_id);

    DROP POLICY IF EXISTS "Users can update own orders" ON public.orders;
    CREATE POLICY "Users can update own orders" ON public.orders FOR UPDATE USING (auth.uid() = user_id);
    """,
    """
    -- Trigger for automatic profile creation on user signup
    CREATE OR REPLACE FUNCTION public.handle_new_user()
    RETURNS TRIGGER AS $$
    BEGIN
      INSERT INTO public.profiles (id, email, demo_balance)
      VALUES (new.id, new.email, 1000.00)
      ON CONFLICT (id) DO UPDATE SET email = EXCLUDED.email;
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql SECURITY DEFINER;

    DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
    CREATE TRIGGER on_auth_user_created
      AFTER INSERT ON auth.users
      FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
    """,
    """
    -- Grant permissions
    GRANT ALL ON public.profiles TO anon, authenticated, service_role;
    GRANT ALL ON public.orders TO anon, authenticated, service_role;
    """
]

print("Applying migrations to Supabase database...")
for stmt in sql_statements:
    conn.run(stmt)
print("Migrations successfully applied!")

tables = conn.run("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
print("Active public tables:", [t[0] for t in tables])
conn.close()
