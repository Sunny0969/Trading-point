import { useState, useEffect } from "react";

type IconName =
  | "search"
  | "bell"
  | "trend"
  | "chart"
  | "trade"
  | "news"
  | "ideas"
  | "plus"
  | "minus";

function Icon({ name, size = 18 }: { name: IconName; size?: number }) {
  const paths: Record<IconName, React.ReactNode> = {
    search: <><circle cx="11" cy="11" r="7" /><path d="m20 20-4-4" /></>,
    bell: <><path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9" /><path d="M10 21h4" /></>,
    trend: <><path d="m4 16 5-5 4 4 7-8" /><path d="M15 7h5v5" /></>,
    chart: <><path d="M4 19V9M10 16V5M16 19v-7M22 13V3" /><path d="M2 22h22" /></>,
    trade: <><path d="M7 7h14l-4-4M21 7l-4 4M17 17H3l4 4M3 17l4-4" /></>,
    news: <><path d="M5 3h14v18H5z" /><path d="M8 7h8M8 11h8M8 15h5" /></>,
    ideas: <><path d="M9 18h6M10 22h4" /><path d="M8 14a7 7 0 1 1 8 0c-1 1-1 2-1 2H9s0-1-1-2Z" /></>,
    plus: <><path d="M12 5v14M5 12h14" /></>,
    minus: <path d="M5 12h14" />,
  };
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {paths[name]}
    </svg>
  );
}

export default function App() {
  const [view, setView] = useState<"dashboard" | "terminal">("dashboard");
  const [timeframe, setTimeframe] = useState("15m");
  const [livePrice, setLivePrice] = useState(4007.05);
  const [changePct, setChangePct] = useState(-0.56);
  const [high24, setHigh24] = useState(4031.5);
  const [low24, setLow24] = useState(3979.42);
  const [macroDrivers, setMacroDrivers] = useState<any[]>([
    { name: "USD Index", value: "101.75", delta: "+0.13%", direction: "up", correlation: "-0.82" },
    { name: "US 10Y", value: "4.28%", delta: "+0.04", direction: "up", correlation: "-0.61" },
    { name: "Crude Oil", value: "$78.39", delta: "+0.80%", direction: "up", correlation: "+0.34" },
    { name: "Silver", value: "$53.90", delta: "-1.26%", direction: "down", correlation: "+0.76" },
    { name: "Real Yields", value: "1.84%", delta: "-0.04", direction: "down", correlation: "-0.71" },
  ]);

  useEffect(() => {
    async function syncData() {
      try {
        const res = await fetch("/api/gold/live");
        if (res.ok) {
          const d = await res.json();
          setLivePrice(d.price);
          setChangePct(d.change_pct);
          setHigh24(d.high);
          setLow24(d.low);
        }
      } catch (e) {}

      try {
        const resD = await fetch("/api/macro/drivers");
        if (resD.ok) {
          const dList = await resD.json();
          if (Array.isArray(dList) && dList.length > 0) setMacroDrivers(dList);
        }
      } catch (e) {}
    }

    syncData();
    const interval = setInterval(syncData, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="app-shell">
      {/* Navbar */}
      <header className="navbar">
        <div className="brand" onClick={() => setView("dashboard")} style={{ cursor: "pointer" }}>
          <span className="brand-mark">Au</span>
          <span>
            XAU<span className="muted">/USD</span>
          </span>
        </div>

        {/* View Switcher */}
        <div className="view-switcher" style={{ display: "flex", gap: "6px" }}>
          <button
            className={`view-btn ${view === "dashboard" ? "active" : ""}`}
            onClick={() => setView("dashboard")}
          >
            🏠 Overview Dashboard
          </button>
          <button
            className={`view-btn ${view === "terminal" ? "active" : ""}`}
            onClick={() => setView("terminal")}
          >
            📊 Deep Analysis Terminal
          </button>
        </div>

        <nav className="timeframes" aria-label="Chart timeframe">
          {["5m", "15m", "1H", "4H", "1D", "1W"].map((t) => (
            <button
              key={t}
              className={timeframe === t ? "active" : ""}
              onClick={() => setTimeframe(t)}
            >
              {t}
            </button>
          ))}
        </nav>

        <div className="nav-actions">
          <button className="insights" onClick={() => setView("terminal")}>
            <Icon name="ideas" size={15} /> Open Terminal &rarr;
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main>
        {view === "dashboard" ? (
          <div>
            {/* Price Hero */}
            <section className="price-hero">
              <div>
                <div className="eyebrow">
                  <span className="live-dot" /> GOLD SPOT · USD{" "}
                  <span className="market-open">ACTIVE TRADING</span>
                </div>
                <div className="price-line">
                  <h1>${livePrice.toFixed(2)}</h1>
                  <span className="currency">USD</span>
                  <span
                    className="change"
                    style={{ color: changePct >= 0 ? "var(--green)" : "var(--red)" }}
                  >
                    {changePct >= 0 ? "+" : ""}
                    {changePct.toFixed(2)}%
                  </span>
                </div>
                <div className="price-sub">Synchronized real-time TradingView feed</div>
              </div>
              <svg className="sparkline" viewBox="0 0 240 70">
                <path d="M2 57 C25 62 27 37 48 44S75 54 90 36s28 5 45-8 26-10 38-4 32-22 63-20" />
              </svg>
              <div className="market-metrics">
                <div><span>24H HIGH</span><b>${high24.toFixed(2)}</b></div>
                <div><span>24H LOW</span><b>${low24.toFixed(2)}</b></div>
                <div><span>24H RANGE</span><b>${(high24 - low24).toFixed(2)}</b></div>
              </div>
            </section>

            {/* Featured CTA Gateway Card to Analysis Terminal */}
            <section className="hero-gateway-card" style={{
              margin: "16px 0 24px",
              padding: "24px 28px",
              borderRadius: "var(--radius)",
              background: "linear-gradient(135deg, rgba(255,215,0,.08), rgba(22,23,19,.85))",
              border: "1px solid rgba(255,215,0,.28)",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center"
            }}>
              <div>
                <div style={{ color: "var(--gold)", fontWeight: 700, fontSize: "10px", letterSpacing: "1px" }}>
                  ⚡ ADVANCED AI & TECHNICAL ANALYSIS ENGINE
                </div>
                <h2 style={{ fontSize: "22px", fontFamily: "Space Grotesk", margin: "6px 0", color: "#fff" }}>
                  Deep Technical Setup, Ghost Candlestick Prediction & Macro Radar
                </h2>
                <p style={{ color: "var(--muted)", fontSize: "12px" }}>
                  Access real-time 15M/1H/4H/1D UT Bot buy/sell triggers, forward 3-candle projection trajectories, safe-haven war escalation radar, and exact SL/TP setups.
                </p>
              </div>
              <button
                onClick={() => setView("terminal")}
                style={{
                  padding: "14px 26px",
                  borderRadius: "14px",
                  fontWeight: 700,
                  fontSize: "14px",
                  fontFamily: "Space Grotesk",
                  color: "var(--bg)",
                  background: "linear-gradient(135deg, var(--gold), #d4af37)",
                  cursor: "pointer",
                  whiteSpace: "nowrap"
                }}
              >
                OPEN ADVANCED ANALYSIS ENGINE &rarr;
              </button>
            </section>

            {/* Macro Drivers */}
            <section className="research-grid">
              <article className="card drivers-card" style={{ width: "100%" }}>
                <div className="section-title">
                  <div>
                    <span className="kicker">MACRO PULSE</span>
                    <h2>Gold Drivers (Intermarket Correlations)</h2>
                  </div>
                </div>
                <div className="driver-grid">
                  {macroDrivers.map((d) => (
                    <div className="driver" key={d.name}>
                      <span>{d.name}</span>
                      <b>{d.value}</b>
                      <small className={d.direction}>
                        {d.direction === "up" ? "↗" : "↘"} {d.delta}
                      </small>
                      <em>Correlation {d.correlation}</em>
                    </div>
                  ))}
                </div>
              </article>
            </section>
          </div>
        ) : (
          /* Terminal View */
          <div style={{ marginTop: "20px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "14px" }}>
              <button
                onClick={() => setView("dashboard")}
                style={{
                  background: "#21262d",
                  border: "1px solid #30363d",
                  color: "var(--gold)",
                  padding: "8px 16px",
                  borderRadius: "10px",
                  cursor: "pointer",
                  fontWeight: 600,
                }}
              >
                &larr; Back to Overview Dashboard
              </button>
              <div style={{ color: "var(--gold)", fontWeight: 700 }}>
                ⚡ Deep Technical & AI Prediction Terminal Active
              </div>
            </div>
            {/* Embedded Live Web Terminal Frame */}
            <iframe
              src="/gold_dashboard.html"
              style={{
                width: "100%",
                height: "calc(100vh - 160px)",
                border: "1px solid var(--line)",
                borderRadius: "var(--radius)",
                background: "#0d1117",
              }}
              title="Gold Terminal"
            />
          </div>
        )}
      </main>
    </div>
  );
}
