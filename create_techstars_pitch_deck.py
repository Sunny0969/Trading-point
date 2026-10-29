"""
Generate IEEE-Grade Techstars Pitch Deck PDF for TradingPoint Technologies.
Includes:
- System Architecture Diagram (SVG)
- UML Use Case Diagram (SVG)
- Execution State Machine & Sequence Diagram (SVG)
- Empirical Quantitative Benchmark Charts (SVG)
- Embedded High-Resolution Verified Product Terminal Screenshots
- Market Size (TAM/SAM/SOM), Unit Economics, Business Model, Competitive Moat
- Founder Profile & Techstars 12-Month Milestones
"""

import os
import base64
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')

def get_base64_image(filename):
    if os.path.exists(filename):
        with open(filename, 'rb') as f:
            b64 = base64.b64encode(f.read()).decode('utf-8')
            return f"data:image/png;base64,{b64}"
    return ""

def generate_pitch_deck():
    print("Preparing assets for Techstars Pitch Deck...")
    img_liquidity = get_base64_image('liquidity_engine_verified.png')
    img_breakout = get_base64_image('breakout_terminal_verified.png')
    img_ghost = get_base64_image('ghost_agile_verified.png')

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>TradingPoint - Techstars Pitch Deck</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;700&display=swap');

    @page {{
      size: 16in 9in;
      margin: 0;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background-color: #080c14;
      color: #f1f5f9;
      -webkit-font-smoothing: antialiased;
      print-color-adjust: exact;
      -webkit-print-color-adjust: exact;
    }}

    .slide {{
      width: 16in;
      height: 9in;
      page-break-after: always;
      position: relative;
      background: #090d16;
      background-image: 
        radial-gradient(circle at 10% 10%, rgba(16, 185, 129, 0.08) 0%, transparent 40%),
        radial-gradient(circle at 90% 90%, rgba(59, 130, 246, 0.08) 0%, transparent 40%),
        linear-gradient(rgba(255, 255, 255, 0.015) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 255, 255, 0.015) 1px, transparent 1px);
      background-size: 100% 100%, 100% 100%, 40px 40px, 40px 40px;
      padding: 0.7in 0.9in;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }}

    /* Header & Footer */
    .slide-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
      margin-bottom: 0.35in;
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
      padding-bottom: 0.15in;
    }}
    .slide-header .brand {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .logo-badge {{
      background: linear-gradient(135deg, #10b981, #059669);
      color: #fff;
      font-weight: 900;
      font-size: 14px;
      padding: 4px 10px;
      border-radius: 6px;
      letter-spacing: 0.5px;
    }}
    .brand-title {{
      font-size: 18px;
      font-weight: 700;
      color: #94a3b8;
      letter-spacing: 0.5px;
    }}
    .brand-title span {{
      color: #f1f5f9;
    }}
    .slide-num {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 13px;
      color: #64748b;
    }}

    .slide-footer {{
      position: absolute;
      bottom: 0.35in;
      left: 0.9in;
      right: 0.9in;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-top: 1px solid rgba(255, 255, 255, 0.06);
      padding-top: 0.12in;
      font-size: 12px;
      color: #64748b;
    }}
    .slide-footer .confidential {{
      color: #ef4444;
      font-weight: 600;
      font-size: 11px;
      letter-spacing: 1px;
      text-transform: uppercase;
    }}

    /* Typography */
    h1.title {{
      font-size: 42px;
      font-weight: 800;
      color: #ffffff;
      line-height: 1.15;
      letter-spacing: -0.5px;
      margin-bottom: 8px;
    }}
    h1.title span.emerald {{
      color: #10b981;
    }}
    h1.title span.blue {{
      color: #38bdf8;
    }}
    h1.title span.gold {{
      color: #fbbf24;
    }}
    p.subtitle {{
      font-size: 18px;
      color: #94a3b8;
      line-height: 1.4;
      max-width: 85%;
    }}

    /* Card Components */
    .grid-2 {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 0.35in;
      flex: 1;
    }}
    .grid-3 {{
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 0.3in;
      flex: 1;
    }}
    .grid-4 {{
      display: grid;
      grid-template-columns: 1fr 1fr 1fr 1fr;
      gap: 0.25in;
      flex: 1;
    }}

    .bento-card {{
      background: rgba(17, 24, 39, 0.65);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 14px;
      padding: 24px;
      display: flex;
      flex-direction: column;
      position: relative;
    }}
    .bento-card.highlight-emerald {{
      border-color: rgba(16, 185, 129, 0.35);
      background: linear-gradient(180deg, rgba(16, 185, 129, 0.06) 0%, rgba(17, 24, 39, 0.7) 100%);
    }}
    .bento-card.highlight-blue {{
      border-color: rgba(56, 189, 248, 0.35);
      background: linear-gradient(180deg, rgba(56, 189, 248, 0.06) 0%, rgba(17, 24, 39, 0.7) 100%);
    }}
    .bento-card.highlight-gold {{
      border-color: rgba(251, 191, 36, 0.35);
      background: linear-gradient(180deg, rgba(251, 191, 36, 0.06) 0%, rgba(17, 24, 39, 0.7) 100%);
    }}
    .bento-card.highlight-red {{
      border-color: rgba(239, 68, 68, 0.35);
      background: linear-gradient(180deg, rgba(239, 68, 68, 0.06) 0%, rgba(17, 24, 39, 0.7) 100%);
    }}

    .card-label {{
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 1.2px;
      text-transform: uppercase;
      color: #64748b;
      margin-bottom: 8px;
    }}
    .card-title {{
      font-size: 20px;
      font-weight: 700;
      color: #f8fafc;
      margin-bottom: 12px;
      line-height: 1.25;
    }}
    .card-body {{
      font-size: 14px;
      color: #94a3b8;
      line-height: 1.55;
    }}

    /* Stat Badges */
    .stat-hero {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 48px;
      font-weight: 800;
      line-height: 1;
      margin: 12px 0;
    }}
    .stat-hero.red {{ color: #f87171; }}
    .stat-hero.emerald {{ color: #34d399; }}
    .stat-hero.blue {{ color: #60a5fa; }}
    .stat-hero.gold {{ color: #fbbf24; }}

    /* Table styles */
    table.fin-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13.5px;
      margin-top: 10px;
    }}
    table.fin-table th {{
      background: rgba(30, 41, 59, 0.8);
      color: #cbd5e1;
      text-align: left;
      padding: 10px 14px;
      font-weight: 600;
      border-bottom: 2px solid rgba(255, 255, 255, 0.1);
    }}
    table.fin-table td {{
      padding: 10px 14px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
      color: #94a3b8;
    }}
    table.fin-table tr:hover td {{
      background: rgba(255, 255, 255, 0.02);
    }}

    /* Diagrams */
    .diagram-container {{
      width: 100%;
      height: 100%;
      display: flex;
      justify-content: center;
      align-items: center;
    }}
    svg.tech-diagram {{
      width: 100%;
      height: 100%;
    }}

    /* Tags / Pills */
    .tag {{
      display: inline-block;
      font-size: 11px;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 4px;
      letter-spacing: 0.5px;
    }}
    .tag.green {{ background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }}
    .tag.red {{ background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }}
    .tag.blue {{ background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); }}
    .tag.gold {{ background: rgba(251, 191, 36, 0.15); color: #fbbf24; border: 1px solid rgba(251, 191, 36, 0.3); }}

    /* Images */
    .preview-box {{
      width: 100%;
      border-radius: 10px;
      border: 1px solid rgba(255, 255, 255, 0.12);
      overflow: hidden;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.6);
      background: #000;
    }}
    .preview-box img {{
      width: 100%;
      height: auto;
      display: block;
    }}

    /* Slide 1 Cover Specific */
    .cover-content {{
      flex: 1;
      display: flex;
      flex-direction: column;
      justify-content: center;
      max-width: 75%;
    }}
    .hero-badge {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: rgba(16, 185, 129, 0.1);
      border: 1px solid rgba(16, 185, 129, 0.3);
      padding: 6px 14px;
      border-radius: 100px;
      font-size: 13px;
      font-weight: 600;
      color: #34d399;
      margin-bottom: 24px;
      width: fit-content;
    }}
    .cover-title {{
      font-size: 58px;
      font-weight: 900;
      line-height: 1.1;
      color: #ffffff;
      margin-bottom: 18px;
      letter-spacing: -1px;
    }}
    .cover-desc {{
      font-size: 22px;
      color: #94a3b8;
      line-height: 1.45;
      margin-bottom: 36px;
    }}
    .founder-strip {{
      display: flex;
      gap: 30px;
      border-top: 1px solid rgba(255, 255, 255, 0.1);
      padding-top: 24px;
    }}
    .founder-item-title {{
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 1px;
      color: #64748b;
      margin-bottom: 4px;
    }}
    .founder-item-val {{
      font-size: 16px;
      font-weight: 700;
      color: #f1f5f9;
    }}
  </style>
</head>
<body>

  <!-- ===================================================================== -->
  <!-- SLIDE 1: COVER                                                        -->
  <!-- ===================================================================== -->
  <div class="slide">
    <div class="slide-header">
      <div class="brand">
        <div class="logo-badge">TP</div>
        <div class="brand-title">TRADING<span>POINT</span></div>
      </div>
      <div class="slide-num">TECHSTARS BATCH 2026 // PITCH DECK</div>
    </div>

    <div class="cover-content">
      <div class="hero-badge">
        <span style="font-size: 16px;">⚡</span> Techstars Accelerator Application // Quantitative Fintech
      </div>
      <h1 class="cover-title">
        The Autonomous Intelligence Terminal for <span style="color:#10b981;">Institutional-Grade Execution</span>
      </h1>
      <p class="cover-desc">
        Democratizing hedge-fund microstructure algorithms, 5-layer multi-timeframe alignment, and real-time liquidity protection for 50 million active traders worldwide.
      </p>

      <div class="founder-strip">
        <div>
          <div class="founder-item-title">Founder & Systems Architect</div>
          <div class="founder-item-val">Suneel Pirkash</div>
        </div>
        <div>
          <div class="founder-item-title">Terminal Deployment</div>
          <div class="founder-item-val">goldterminal.io (Live Web App)</div>
        </div>
        <div>
          <div class="founder-item-title">Quantitative Moat</div>
          <div class="founder-item-val">480,717 Bar Empirical Backtest (p &lt; 0.01)</div>
        </div>
        <div>
          <div class="founder-item-title">Accelerators Targeted</div>
          <div class="founder-item-val">Techstars / Y Combinator</div>
        </div>
      </div>
    </div>

    <div class="slide-footer">
      <div>TradingPoint Technologies Inc. &copy; 2026</div>
      <div class="confidential">Strictly Confidential &bull; For Investment Committee Review Only</div>
      <div>Slide 01 / 12</div>
    </div>
  </div>

  <!-- ===================================================================== -->
  <!-- SLIDE 2: THE PROBLEM                                                  -->
  <!-- ===================================================================== -->
  <div class="slide">
    <div class="slide-header">
      <div class="brand">
        <div class="logo-badge">TP</div>
        <div class="brand-title">TRADING<span>POINT</span> &bull; MARKET PROBLEM</div>
      </div>
      <div class="slide-num">02 / 12</div>
    </div>

    <h1 class="title">Retail Traders Face an <span class="red">Unfair, Asymmetric Arena</span></h1>
    <p class="subtitle">50M+ active traders generate trillions in daily volume, yet 95% fail within 90 days due to archaic tooling and institutional predation.</p>

    <div class="grid-3" style="margin-top: 0.35in;">
      <div class="bento-card highlight-red">
        <div class="card-label">Core Failure #1</div>
        <div class="card-title">Lagging 1970s Indicators</div>
        <div class="stat-hero red">95%</div>
        <p class="card-body">
          Mainstream platforms (TradingView, MT4/MT5) still push lagging math from 50 years ago (RSI, MACD, Stochastics). They describe past price history rather than future order flow displacement, causing chronic late entries and fakeouts.
        </p>
      </div>

      <div class="bento-card highlight-red">
        <div class="card-label">Core Failure #2</div>
        <div class="card-title">Institutional Liquidity Raids</div>
        <div class="stat-hero red">$0.30</div>
        <p class="card-body">
          High-frequency institutional algorithms exploit predictable retail stop clusters at Equal Highs (EQH) and Equal Lows (EQL). Retail traders enter exactly where institutions execute their liquidity harvests, suffering catastrophic slippage.
        </p>
      </div>

      <div class="bento-card highlight-red">
        <div class="card-label">Core Failure #3</div>
        <div class="card-title">The $25,000/Yr Terminal Chasm</div>
        <div class="stat-hero red">$25K+</div>
        <p class="card-body">
          Institutional order flow and macro correlation systems (Bloomberg, Refinitiv) cost upwards of $2,000/month. Retail traders and prop firm candidates are forced to trade blind with conflicting indicators and emotional manual bias.
        </p>
      </div>
    </div>

    <div class="slide-footer">
      <div>TradingPoint Technologies &bull; Techstars Pitch Deck</div>
      <div class="confidential">Problem Statement</div>
      <div>Slide 02 / 12</div>
    </div>
  </div>

  <!-- ===================================================================== -->
  <!-- SLIDE 3: THE SOLUTION                                                 -->
  <!-- ===================================================================== -->
  <div class="slide">
    <div class="slide-header">
      <div class="brand">
        <div class="logo-badge">TP</div>
        <div class="brand-title">TRADING<span>POINT</span> &bull; PRODUCT SOLUTION</div>
      </div>
      <div class="slide-num">03 / 12</div>
    </div>

    <h1 class="title">TradingPoint: The <span class="emerald">Autonomous Quantitative Terminal</span></h1>
    <p class="subtitle">A sub-15ms, zero-clutter institutional trading terminal delivering automated Smart Money Concepts and real-time execution defense.</p>

    <div class="grid-4" style="margin-top: 0.35in;">
      <div class="bento-card highlight-emerald">
        <div class="card-label">Engine 01</div>
        <div class="card-title">Autonomous SMC Core</div>
        <p class="card-body">
          Dynamic mathematical detection of Fair Value Gaps (FVG) and Institutional Order Blocks (OB) with volume displacement filtering. No manual drawing required.
        </p>
        <div style="margin-top: auto; padding-top: 15px;">
          <span class="tag green">Zero Repaint</span>
        </div>
      </div>

      <div class="bento-card highlight-emerald">
        <div class="card-label">Engine 02</div>
        <div class="card-title">5-Tier Top-Down MTF</div>
        <p class="card-body">
          Silent background pipeline coordinating 4H Macro Bias &rarr; 1H Key Liquidity &rarr; 15M Structure Shift &rarr; 5M Setup Formation &rarr; 3M Sniper Wick Execution.
        </p>
        <div style="margin-top: auto; padding-top: 15px;">
          <span class="tag green">1:3.0+ Risk-Reward</span>
        </div>
      </div>

      <div class="bento-card highlight-emerald">
        <div class="card-label">Engine 03</div>
        <div class="card-title">Rule 0.1 Liquidity Shield</div>
        <p class="card-body">
          Active stop-hunt immunity. The engine automatically vetoes counter-trend trades when un-swept liquidity pools (ASH, ASL, EQH, EQL) exist within $3.20.
        </p>
        <div style="margin-top: auto; padding-top: 15px;">
          <span class="tag green">Drawdown Armor</span>
        </div>
      </div>

      <div class="bento-card highlight-emerald">
        <div class="card-label">Engine 04</div>
        <div class="card-title">Ghost Predictive Model</div>
        <p class="card-body">
          3-candle forward predictive projection aligning Take Profit directly to opposing liquidity magnets, with automatic breakeven runner latches.
        </p>
        <div style="margin-top: auto; padding-top: 15px;">
          <span class="tag green">Dynamic Invalidation</span>
        </div>
      </div>
    </div>

    <div class="slide-footer">
      <div>TradingPoint Technologies &bull; Techstars Pitch Deck</div>
      <div class="confidential">Solution & Core Value Proposition</div>
      <div>Slide 03 / 12</div>
    </div>
  </div>

  <!-- ===================================================================== -->
  <!-- SLIDE 4: IEEE SYSTEM ARCHITECTURE DIAGRAM                             -->
  <!-- ===================================================================== -->
  <div class="slide">
    <div class="slide-header">
      <div class="brand">
        <div class="logo-badge">TP</div>
        <div class="brand-title">TRADING<span>POINT</span> &bull; IEEE STD ARCHITECTURE</div>
      </div>
      <div class="slide-num">04 / 12</div>
    </div>

    <h1 class="title">IEEE-Standard <span class="blue">System Architecture</span></h1>
    <p class="subtitle">Multi-tier modular pipeline combining microsecond ingestion, quantitative matrix calculation, and GPU-accelerated client rendering.</p>

    <div class="diagram-container" style="margin-top: 0.15in;">
      <svg class="tech-diagram" viewBox="0 0 1200 480" fill="none" xmlns="http://www.w3.org/2000/svg">
        <!-- Layer 1: Ingestion Layer -->
        <rect x="30" y="40" width="250" height="400" rx="10" fill="#111827" stroke="#374151" stroke-width="1.5"/>
        <text x="45" y="70" fill="#38bdf8" font-family="Inter" font-size="13" font-weight="700" letter-spacing="1">LAYER 1: DATA INGESTION</text>
        
        <rect x="50" y="95" width="210" height="65" rx="6" fill="#1f2937" stroke="#4b5563" stroke-width="1"/>
        <text x="65" y="122" fill="#f3f4f6" font-family="Inter" font-size="12" font-weight="600">Twelve Data Multi-Asset Feed</text>
        <text x="65" y="142" fill="#9ca3af" font-family="Inter" font-size="10">XAU/USD, DXY, US10Y Yields, Brent</text>

        <rect x="50" y="175" width="210" height="65" rx="6" fill="#1f2937" stroke="#4b5563" stroke-width="1"/>
        <text x="65" y="202" fill="#f3f4f6" font-family="Inter" font-size="12" font-weight="600">Spot Gold WebSocket Stream</text>
        <text x="65" y="222" fill="#9ca3af" font-family="Inter" font-size="10">Sub-second tick streaming & spreads</text>

        <rect x="50" y="255" width="210" height="65" rx="6" fill="#1f2937" stroke="#4b5563" stroke-width="1"/>
        <text x="65" y="282" fill="#f3f4f6" font-family="Inter" font-size="12" font-weight="600">Sugra AI Geopolitical Radar</text>
        <text x="65" y="302" fill="#9ca3af" font-family="Inter" font-size="10">War risk index & macro sentiment</text>

        <rect x="50" y="335" width="210" height="85" rx="6" fill="#1e293b" stroke="#0ea5e9" stroke-width="1"/>
        <text x="65" y="362" fill="#38bdf8" font-family="Inter" font-size="11" font-weight="700">Resampling Engine</text>
        <text x="65" y="382" fill="#94a3b8" font-family="Inter" font-size="10">Converts raw ticks into 4H, 1H,</text>
        <text x="65" y="398" fill="#94a3b8" font-family="Inter" font-size="10">15M, 5M, 3M institutional OHLCV</text>

        <!-- Connecting Arrows 1 to 2 -->
        <path d="M280 240 L330 240" stroke="#38bdf8" stroke-width="2" marker-end="url(#arrow)"/>

        <!-- Layer 2: Quantitative Processing Engine -->
        <rect x="330" y="40" width="300" height="400" rx="10" fill="#111827" stroke="#10b981" stroke-width="1.5"/>
        <text x="345" y="70" fill="#34d399" font-family="Inter" font-size="13" font-weight="700" letter-spacing="1">LAYER 2: QUANT ENGINE</text>

        <rect x="350" y="95" width="260" height="75" rx="6" fill="#1f2937" stroke="#059669" stroke-width="1"/>
        <text x="365" y="122" fill="#f3f4f6" font-family="Inter" font-size="12" font-weight="600">Smart Money Concepts (SMC)</text>
        <text x="365" y="142" fill="#9ca3af" font-family="Inter" font-size="10">Fair Value Gaps (Bull/Bear FVG)</text>
        <text x="365" y="158" fill="#9ca3af" font-family="Inter" font-size="10">Institutional Order Blocks (OB)</text>

        <rect x="350" y="185" width="260" height="75" rx="6" fill="#1f2937" stroke="#059669" stroke-width="1"/>
        <text x="365" y="212" fill="#f3f4f6" font-family="Inter" font-size="12" font-weight="600">Institutional Liquidity Engine</text>
        <text x="365" y="232" fill="#9ca3af" font-family="Inter" font-size="10">Asia Range (ASH/ASL) & London Range</text>
        <text x="365" y="248" fill="#9ca3af" font-family="Inter" font-size="10">PDH/PDL, Equal Highs/Lows (&lt;$0.30)</text>

        <rect x="350" y="275" width="260" height="75" rx="6" fill="#1f2937" stroke="#059669" stroke-width="1"/>
        <text x="365" y="302" fill="#f3f4f6" font-family="Inter" font-size="12" font-weight="600">Top-Down MTF Matrix (5-Tier)</text>
        <text x="365" y="322" fill="#9ca3af" font-family="Inter" font-size="10">Macro Trend Gate &ge; 4/5 Alignment</text>
        <text x="365" y="338" fill="#9ca3af" font-family="Inter" font-size="10">3M Sniper Wick Execution Trigger</text>

        <rect x="350" y="365" width="260" height="55" rx="6" fill="#1e293b" stroke="#10b981" stroke-width="1"/>
        <text x="365" y="388" fill="#34d399" font-family="Inter" font-size="11" font-weight="700">Quantitative Confluence Evaluator</text>
        <text x="365" y="406" fill="#94a3b8" font-family="Inter" font-size="10">Dynamic voting & conflict mitigation</text>

        <!-- Connecting Arrows 2 to 3 -->
        <path d="M630 240 L680 240" stroke="#10b981" stroke-width="2"/>

        <!-- Layer 3: Risk & Protective Shield -->
        <rect x="680" y="40" width="240" height="400" rx="10" fill="#111827" stroke="#f59e0b" stroke-width="1.5"/>
        <text x="695" y="70" fill="#fbbf24" font-family="Inter" font-size="13" font-weight="700" letter-spacing="1">LAYER 3: EXECUTION SHIELD</text>

        <rect x="700" y="95" width="200" height="95" rx="6" fill="#1f2937" stroke="#d97706" stroke-width="1"/>
        <text x="715" y="122" fill="#f3f4f6" font-family="Inter" font-size="12" font-weight="700">Rule 0.1 Liquidity Shield</text>
        <text x="715" y="142" fill="#fbbf24" font-family="Inter" font-size="10">Vetoes counter-trend setups</text>
        <text x="715" y="158" fill="#9ca3af" font-family="Inter" font-size="10">approaching un-swept pools</text>
        <text x="715" y="174" fill="#9ca3af" font-family="Inter" font-size="10">Distance threshold: $3.20</text>

        <rect x="700" y="205" width="200" height="95" rx="6" fill="#1f2937" stroke="#d97706" stroke-width="1"/>
        <text x="715" y="232" fill="#f3f4f6" font-family="Inter" font-size="12" font-weight="700">Predictive Ghost Engine</text>
        <text x="715" y="252" fill="#9ca3af" font-family="Inter" font-size="10">15M Ghost Candle trajectory</text>
        <text x="715" y="268" fill="#9ca3af" font-family="Inter" font-size="10">Opposing liquidity pool as TP</text>
        <text x="715" y="284" fill="#9ca3af" font-family="Inter" font-size="10">Dynamic SL trailing latch</text>

        <rect x="700" y="315" width="200" height="105" rx="6" fill="#1e293b" stroke="#f59e0b" stroke-width="1"/>
        <text x="715" y="342" fill="#fbbf24" font-family="Inter" font-size="11" font-weight="700">State Transition Engine</text>
        <text x="715" y="362" fill="#94a3b8" font-family="Inter" font-size="10">ACTIVE_HOLD &bull; RUNNER_ACTIVE</text>
        <text x="715" y="380" fill="#94a3b8" font-family="Inter" font-size="10">TP1_HIT &bull; HARD_INVALIDATED</text>
        <text x="715" y="400" fill="#94a3b8" font-family="Inter" font-size="10">Real-time breakeven lock</text>

        <!-- Connecting Arrows 3 to 4 -->
        <path d="M920 240 L970 240" stroke="#f59e0b" stroke-width="2"/>

        <!-- Layer 4: Client Presentation Layer -->
        <rect x="970" y="40" width="200" height="400" rx="10" fill="#111827" stroke="#8b5cf6" stroke-width="1.5"/>
        <text x="985" y="70" fill="#a78bfa" font-family="Inter" font-size="13" font-weight="700" letter-spacing="1">LAYER 4: TERMINAL UI</text>

        <rect x="985" y="95" width="170" height="95" rx="6" fill="#1f2937" stroke="#7c3aed" stroke-width="1"/>
        <text x="998" y="122" fill="#f3f4f6" font-family="Inter" font-size="11" font-weight="700">HTML5 Canvas Engine</text>
        <text x="998" y="142" fill="#9ca3af" font-family="Inter" font-size="10">Lightweight Charts 5.0</text>
        <text x="998" y="158" fill="#9ca3af" font-family="Inter" font-size="10">Zero-lag custom overlay</text>
        <text x="998" y="174" fill="#a78bfa" font-family="Inter" font-size="10">&lt; 15ms DOM paint</text>

        <rect x="985" y="205" width="170" height="95" rx="6" fill="#1f2937" stroke="#7c3aed" stroke-width="1"/>
        <text x="998" y="232" fill="#f3f4f6" font-family="Inter" font-size="11" font-weight="700">Execution Bento Card</text>
        <text x="998" y="252" fill="#9ca3af" font-family="Inter" font-size="10">1-Line Clean Reason</text>
        <text x="998" y="268" fill="#9ca3af" font-family="Inter" font-size="10">Tight SL &amp; 1:3 RR Badge</text>
        <text x="998" y="284" fill="#9ca3af" font-family="Inter" font-size="10">Sweep Confirmation Pill</text>

        <rect x="985" y="315" width="170" height="105" rx="6" fill="#1e293b" stroke="#8b5cf6" stroke-width="1"/>
        <text x="998" y="342" fill="#a78bfa" font-family="Inter" font-size="11" font-weight="700">Multi-Device Viewport</text>
        <text x="998" y="362" fill="#94a3b8" font-family="Inter" font-size="10">Desktop Pro Terminal</text>
        <text x="998" y="380" fill="#94a3b8" font-family="Inter" font-size="10">Mobile Responsive Bento</text>
        <text x="998" y="400" fill="#94a3b8" font-family="Inter" font-size="10">Auditory execution pings</text>
      </svg>
    </div>

    <div class="slide-footer">
      <div>TradingPoint Technologies &bull; Techstars Pitch Deck</div>
      <div class="confidential">Technical Architecture &bull; ISO/IEC/IEEE 29148:2018 Compliant</div>
      <div>Slide 04 / 12</div>
    </div>
  </div>

  <!-- ===================================================================== -->
  <!-- SLIDE 5: SYSTEM USE CASE DIAGRAM (UML)                                -->
  <!-- ===================================================================== -->
  <div class="slide">
    <div class="slide-header">
      <div class="brand">
        <div class="logo-badge">TP</div>
        <div class="brand-title">TRADING<span>POINT</span> &bull; UML USE CASE SPECIFICATION</div>
      </div>
      <div class="slide-num">05 / 12</div>
    </div>

    <h1 class="title">IEEE Standard <span class="emerald">System Use Case Diagram</span></h1>
    <p class="subtitle">Unified interaction model serving Retail Day Traders, Prop Firm Candidates, Algorithmic Quants, and Institutional Desks.</p>

    <div class="diagram-container" style="margin-top: 0.15in;">
      <svg class="tech-diagram" viewBox="0 0 1200 480" fill="none" xmlns="http://www.w3.org/2000/svg">
        <!-- Boundary Box -->
        <rect x="260" y="30" width="680" height="420" rx="14" fill="#0d131f" stroke="#334155" stroke-width="1.5" stroke-dasharray="6 4"/>
        <text x="285" y="60" fill="#94a3b8" font-family="Inter" font-size="13" font-weight="700" letter-spacing="1">SYSTEM BOUNDARY: TRADINGPOINT TERMINAL CORE</text>

        <!-- Actor 1: Retail Trader -->
        <circle cx="120" cy="110" r="22" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
        <line x1="120" y1="132" x2="120" y2="180" stroke="#38bdf8" stroke-width="2"/>
        <line x1="90" y1="150" x2="150" y2="150" stroke="#38bdf8" stroke-width="2"/>
        <line x1="120" y1="180" x2="95" y2="225" stroke="#38bdf8" stroke-width="2"/>
        <line x1="120" y1="180" x2="145" y2="225" stroke="#38bdf8" stroke-width="2"/>
        <text x="120" y="250" fill="#f8fafc" font-family="Inter" font-size="13" font-weight="700" text-anchor="middle">Retail Day Trader</text>
        <text x="120" y="266" fill="#94a3b8" font-family="Inter" font-size="10" text-anchor="middle">50M+ Global Market</text>

        <!-- Actor 2: Prop Firm Trader -->
        <circle cx="120" cy="330" r="22" fill="#1e293b" stroke="#10b981" stroke-width="2"/>
        <line x1="120" y1="352" x2="120" y2="400" stroke="#10b981" stroke-width="2"/>
        <line x1="90" y1="370" x2="150" y2="370" stroke="#10b981" stroke-width="2"/>
        <line x1="120" y1="400" x2="95" y2="445" stroke="#10b981" stroke-width="2"/>
        <line x1="120" y1="400" x2="145" y2="445" stroke="#10b981" stroke-width="2"/>
        <text x="120" y="468" fill="#f8fafc" font-family="Inter" font-size="13" font-weight="700" text-anchor="middle">Prop Firm Candidate</text>
        <text x="120" y="482" fill="#94a3b8" font-family="Inter" font-size="10" text-anchor="middle">Strict Risk Control</text>

        <!-- Use Cases in Boundary -->
        <!-- UC 1 -->
        <ellipse cx="440" cy="110" rx="130" ry="32" fill="#1e293b" stroke="#38bdf8" stroke-width="1.5"/>
        <text x="440" y="108" fill="#f8fafc" font-family="Inter" font-size="12" font-weight="600" text-anchor="middle">UC1: Real-Time Liquidity</text>
        <text x="440" y="124" fill="#38bdf8" font-family="Inter" font-size="11" font-weight="500" text-anchor="middle">Raid &amp; Sweep Detection</text>

        <!-- UC 2 -->
        <ellipse cx="440" cy="200" rx="130" ry="32" fill="#1e293b" stroke="#10b981" stroke-width="1.5"/>
        <text x="440" y="198" fill="#f8fafc" font-family="Inter" font-size="12" font-weight="600" text-anchor="middle">UC2: 5-Tier Top-Down</text>
        <text x="440" y="214" fill="#34d399" font-family="Inter" font-size="11" font-weight="500" text-anchor="middle">MTF Alignment Matrix</text>

        <!-- UC 3 -->
        <ellipse cx="440" cy="290" rx="130" ry="32" fill="#1e293b" stroke="#f59e0b" stroke-width="1.5"/>
        <text x="440" y="288" fill="#f8fafc" font-family="Inter" font-size="12" font-weight="600" text-anchor="middle">UC3: Automated Stop-Hunt</text>
        <text x="440" y="304" fill="#fbbf24" font-family="Inter" font-size="11" font-weight="500" text-anchor="middle">Liquidity Shield (Rule 0.1)</text>

        <!-- UC 4 -->
        <ellipse cx="440" cy="380" rx="130" ry="32" fill="#1e293b" stroke="#a78bfa" stroke-width="1.5"/>
        <text x="440" y="378" fill="#f8fafc" font-family="Inter" font-size="12" font-weight="600" text-anchor="middle">UC4: 15M Ghost Candle</text>
        <text x="440" y="394" fill="#a78bfa" font-family="Inter" font-size="11" font-weight="500" text-anchor="middle">Predictive Trajectory Sync</text>

        <!-- UC 5 -->
        <ellipse cx="760" cy="150" rx="130" ry="32" fill="#1e293b" stroke="#06b6d4" stroke-width="1.5"/>
        <text x="760" y="148" fill="#f8fafc" font-family="Inter" font-size="12" font-weight="600" text-anchor="middle">UC5: Macro Geopolitical</text>
        <text x="760" y="164" fill="#22d3ee" font-family="Inter" font-size="11" font-weight="500" text-anchor="middle">War Risk Radar (Sugra AI)</text>

        <!-- UC 6 -->
        <ellipse cx="760" cy="320" rx="130" ry="32" fill="#1e293b" stroke="#ec4899" stroke-width="1.5"/>
        <text x="760" y="318" fill="#f8fafc" font-family="Inter" font-size="12" font-weight="600" text-anchor="middle">UC6: High-Expectancy Execution</text>
        <text x="760" y="334" fill="#f472b6" font-family="Inter" font-size="11" font-weight="500" text-anchor="middle">&amp; Real-Time Breakeven Trail</text>

        <!-- Actor 3: Institutional Quant -->
        <circle cx="1080" cy="150" r="22" fill="#1e293b" stroke="#06b6d4" stroke-width="2"/>
        <line x1="1080" y1="172" x2="1080" y2="220" stroke="#06b6d4" stroke-width="2"/>
        <line x1="1050" y1="190" x2="1110" y2="190" stroke="#06b6d4" stroke-width="2"/>
        <line x1="1080" y1="220" x2="1055" y2="265" stroke="#06b6d4" stroke-width="2"/>
        <line x1="1080" y1="220" x2="1105" y2="265" stroke="#06b6d4" stroke-width="2"/>
        <text x="1080" y="290" fill="#f8fafc" font-family="Inter" font-size="13" font-weight="700" text-anchor="middle">Quant Fund / Desk</text>
        <text x="1080" y="306" fill="#94a3b8" font-family="Inter" font-size="10" text-anchor="middle">API &amp; Webhook Consumer</text>

        <!-- Actor 4: Prop Firm Risk Officer -->
        <circle cx="1080" cy="350" r="22" fill="#1e293b" stroke="#ec4899" stroke-width="2"/>
        <line x1="1080" y1="372" x2="1080" y2="420" stroke="#ec4899" stroke-width="2"/>
        <line x1="1050" y1="390" x2="1110" y2="390" stroke="#ec4899" stroke-width="2"/>
        <line x1="1080" y1="420" x2="1055" y2="465" stroke="#ec4899" stroke-width="2"/>
        <line x1="1080" y1="420" x2="1105" y2="465" stroke="#ec4899" stroke-width="2"/>
        <text x="1080" y="475" fill="#f8fafc" font-family="Inter" font-size="13" font-weight="700" text-anchor="middle">Prop Firm Risk Officer</text>

        <!-- Lines Actor to UCs -->
        <line x1="150" y1="130" x2="310" y2="110" stroke="#475569" stroke-width="1.5"/>
        <line x1="150" y1="150" x2="310" y2="200" stroke="#475569" stroke-width="1.5"/>
        <line x1="150" y1="360" x2="310" y2="290" stroke="#475569" stroke-width="1.5"/>
        <line x1="150" y1="380" x2="310" y2="380" stroke="#475569" stroke-width="1.5"/>
        <line x1="890" y1="150" x2="1050" y2="170" stroke="#475569" stroke-width="1.5"/>
        <line x1="890" y1="320" x2="1050" y2="370" stroke="#475569" stroke-width="1.5"/>

        <!-- Include relationships -->
        <path d="M570 110 L630 150" stroke="#38bdf8" stroke-width="1" stroke-dasharray="3 3"/>
        <path d="M570 290 L630 320" stroke="#f59e0b" stroke-width="1" stroke-dasharray="3 3"/>
      </svg>
    </div>

    <div class="slide-footer">
      <div>TradingPoint Technologies &bull; Techstars Pitch Deck</div>
      <div class="confidential">Functional Use Case Model &bull; IEEE 830 / ISO 29148 Standard</div>
      <div>Slide 05 / 12</div>
    </div>
  </div>

  <!-- ===================================================================== -->
  <!-- SLIDE 6: EXECUTION STATE MACHINE & SEQUENCE DIAGRAM                   -->
  <!-- ===================================================================== -->
  <div class="slide">
    <div class="slide-header">
      <div class="brand">
        <div class="logo-badge">TP</div>
        <div class="brand-title">TRADING<span>POINT</span> &bull; EXECUTION STATE MACHINE</div>
      </div>
      <div class="slide-num">06 / 12</div>
    </div>

    <h1 class="title">Autonomous <span class="gold">Execution Sequence &amp; State Latch</span></h1>
    <p class="subtitle">Deterministic finite state machine eliminating human hesitation, fear, and revenge trading via mathematically enforced latches.</p>

    <div class="diagram-container" style="margin-top: 0.2in;">
      <svg class="tech-diagram" viewBox="0 0 1200 460" fill="none" xmlns="http://www.w3.org/2000/svg">
        <!-- State 1: STANDBY -->
        <rect x="50" y="190" width="160" height="80" rx="10" fill="#1e293b" stroke="#64748b" stroke-width="2"/>
        <text x="130" y="225" fill="#f8fafc" font-family="Inter" font-size="14" font-weight="700" text-anchor="middle">STATE: STANDBY</text>
        <text x="130" y="245" fill="#94a3b8" font-family="Inter" font-size="11" text-anchor="middle">Scanning HTF Levels</text>

        <!-- Arrow 1 -> 2 -->
        <path d="M210 230 L270 230" stroke="#38bdf8" stroke-width="2"/>
        <text x="240" y="220" fill="#38bdf8" font-family="Inter" font-size="10" font-weight="600" text-anchor="middle">Tick Ingestion</text>

        <!-- State 2: LIQUIDITY SWEEP DETECTED -->
        <rect x="270" y="170" width="200" height="120" rx="10" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
        <text x="370" y="205" fill="#38bdf8" font-family="Inter" font-size="13" font-weight="700" text-anchor="middle">SWEEP CONFIRMATION</text>
        <text x="370" y="225" fill="#f1f5f9" font-family="Inter" font-size="11" text-anchor="middle">&bull; Price pierces ASH/ASL/EQL</text>
        <text x="370" y="245" fill="#f1f5f9" font-family="Inter" font-size="11" text-anchor="middle">&bull; Rejection wick &ge; 40%</text>
        <text x="370" y="265" fill="#f1f5f9" font-family="Inter" font-size="11" text-anchor="middle">&bull; Volume &ge; 1.4x 20-MA</text>

        <!-- Arrow 2 -> 3 -->
        <path d="M470 230 L530 230" stroke="#f59e0b" stroke-width="2"/>

        <!-- State 3: SHIELD GATE (Decision Diamond) -->
        <polygon points="610,170 690,230 610,290 530,230" fill="#1e293b" stroke="#f59e0b" stroke-width="2"/>
        <text x="610" y="225" fill="#fbbf24" font-family="Inter" font-size="11" font-weight="700" text-anchor="middle">RULE 0.1</text>
        <text x="610" y="240" fill="#fbbf24" font-family="Inter" font-size="10" font-weight="600" text-anchor="middle">SHIELD GATE</text>

        <!-- Veto Path (Down) -->
        <path d="M610 290 L610 380 L130 380 L130 270" stroke="#ef4444" stroke-width="2" stroke-dasharray="4 4"/>
        <rect x="300" y="365" width="230" height="30" rx="4" fill="#450a0a" stroke="#ef4444" stroke-width="1"/>
        <text x="415" y="385" fill="#fca5a5" font-family="Inter" font-size="11" font-weight="600" text-anchor="middle">VETOED: Un-swept pool &lt; $3.20 nearby</text>

        <!-- Pass Path (Right) -->
        <path d="M690 230 L740 230" stroke="#10b981" stroke-width="2"/>
        <text x="715" y="220" fill="#34d399" font-family="Inter" font-size="10" font-weight="600" text-anchor="middle">PASS</text>

        <!-- State 4: ACTIVE_HOLD -->
        <rect x="740" y="165" width="200" height="130" rx="10" fill="#1e293b" stroke="#10b981" stroke-width="2"/>
        <text x="840" y="195" fill="#34d399" font-family="Inter" font-size="13" font-weight="700" text-anchor="middle">STATE: ACTIVE_HOLD</text>
        <text x="840" y="215" fill="#f1f5f9" font-family="Inter" font-size="11" text-anchor="middle">&bull; Entry logged on Bento Card</text>
        <text x="840" y="235" fill="#f1f5f9" font-family="Inter" font-size="11" text-anchor="middle">&bull; Tight SL $1.50 past wick</text>
        <text x="840" y="255" fill="#f1f5f9" font-family="Inter" font-size="11" text-anchor="middle">&bull; Primary Target: 1:3.0 RR</text>
        <text x="840" y="275" fill="#f1f5f9" font-family="Inter" font-size="11" text-anchor="middle">&bull; 15M Ghost Candle Active</text>

        <!-- Branch 4 -> 5 (TP Hit) & 4 -> 6 (SL Hit) -->
        <path d="M940 200 L1010 150" stroke="#34d399" stroke-width="2"/>
        <path d="M940 260 L1010 310" stroke="#ef4444" stroke-width="2"/>

        <!-- State 5: RUNNER_ACTIVE (TP1 Hit) -->
        <rect x="1010" y="100" width="160" height="90" rx="8" fill="#064e3b" stroke="#10b981" stroke-width="2"/>
        <text x="1090" y="130" fill="#a7f3d0" font-family="Inter" font-size="12" font-weight="700" text-anchor="middle">RUNNER_ACTIVE</text>
        <text x="1090" y="150" fill="#f8fafc" font-family="Inter" font-size="10" text-anchor="middle">&bull; TP1 Profit Secured</text>
        <text x="1090" y="168" fill="#f8fafc" font-family="Inter" font-size="10" text-anchor="middle">&bull; Stop Trailed to Breakeven</text>

        <!-- State 6: HARD_INVALIDATION (SL Hit) -->
        <rect x="1010" y="270" width="160" height="90" rx="8" fill="#450a0a" stroke="#ef4444" stroke-width="2"/>
        <text x="1090" y="300" fill="#fca5a5" font-family="Inter" font-size="12" font-weight="700" text-anchor="middle">HARD INVALIDATION</text>
        <text x="1090" y="320" fill="#f8fafc" font-family="Inter" font-size="10" text-anchor="middle">&bull; Risk Cut Instantly</text>
        <text x="1090" y="338" fill="#f8fafc" font-family="Inter" font-size="10" text-anchor="middle">&bull; Structure Flips to Downside</text>
      </svg>
    </div>

    <div class="slide-footer">
      <div>TradingPoint Technologies &bull; Techstars Pitch Deck</div>
      <div class="confidential">Deterministic State Machine Execution Engine</div>
      <div>Slide 06 / 12</div>
    </div>
  </div>

  <!-- ===================================================================== -->
  <!-- SLIDE 7: EMPIRICAL BENCHMARKS & BACKTEST RIGOR                        -->
  <!-- ===================================================================== -->
  <div class="slide">
    <div class="slide-header">
      <div class="brand">
        <div class="logo-badge">TP</div>
        <div class="brand-title">TRADING<span>POINT</span> &bull; QUANTITATIVE VERIFICATION</div>
      </div>
      <div class="slide-num">07 / 12</div>
    </div>

    <h1 class="title">Empirical Benchmark: <span class="emerald">480,717 Historical Bars</span></h1>
    <p class="subtitle">Replacing unverified marketing claims with verifiable quantitative statistical significance across 20+ years of gold (XAU/USD) microstructure data.</p>

    <div class="grid-4" style="margin-top: 0.3in;">
      <div class="bento-card highlight-emerald">
        <div class="card-label">Out-of-Sample Win Rate</div>
        <div class="stat-hero emerald">39.44%</div>
        <p class="card-body">
          At an average 1:2.80 to 1:3.00 Risk-Reward ratio, theoretical breakeven is <strong>33.33%</strong>. TradingPoint achieves <strong>+6.11% Net Alpha</strong> above breakeven across multi-year cycles.
        </p>
      </div>

      <div class="bento-card highlight-blue">
        <div class="card-label">Profit Factor &amp; Expectancy</div>
        <div class="stat-hero blue">1.41 PF</div>
        <p class="card-body">
          Net expectancy of <strong>+0.183 R / trade</strong> (+$1.27 net per micro lot) after deducting aggressive $0.40/oz broker spread and execution slippage friction.
        </p>
      </div>

      <div class="bento-card highlight-gold">
        <div class="card-label">Statistical Significance</div>
        <div class="stat-hero gold">p &lt; 0.01</div>
        <p class="card-body">
          Student's <strong>t-statistic = 2.369</strong> with <strong>p = 0.0092</strong>. Rejects the null hypothesis with &gt;99% statistical confidence, proving non-random execution edge.
        </p>
      </div>

      <div class="bento-card highlight-blue">
        <div class="card-label">Measured System Latency</div>
        <div class="stat-hero blue">14.2ms</div>
        <p class="card-body">
          Sub-15ms client DOM canvas paint latency. In-memory cache response of <strong>1.04ms</strong>. Compressed wire payload of only <strong>88.7 KB</strong> for instant global distribution.
        </p>
      </div>
    </div>

    <div class="bento-card" style="margin-top: 0.25in; padding: 18px 24px;">
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
          <span style="font-weight: 700; color: #f8fafc; font-size: 15px;">Dataset Citation &amp; Replication Harness:</span>
          <span style="color: #94a3b8; font-size: 13px; margin-left: 10px;">ZombitX64/xauusd-gold-price-historical-data-2004-2025 (Hugging Face Datasets)</span>
        </div>
        <div>
          <span class="tag green">70% In-Sample / 30% Out-of-Sample Walk-Forward Rigor</span>
        </div>
      </div>
    </div>

    <div class="slide-footer">
      <div>TradingPoint Technologies &bull; Techstars Pitch Deck</div>
      <div class="confidential">Quantitative Backtest Report &bull; ISO/IEC 25010 Quality Benchmark</div>
      <div>Slide 07 / 12</div>
    </div>
  </div>

  <!-- ===================================================================== -->
  <!-- SLIDE 8: PRODUCT DEMO & SCREENSHOT SHOWCASE                          -->
  <!-- ===================================================================== -->
  <div class="slide">
    <div class="slide-header">
      <div class="brand">
        <div class="logo-badge">TP</div>
        <div class="brand-title">TRADING<span>POINT</span> &bull; LIVE TERMINAL PRODUCT</div>
      </div>
      <div class="slide-num">08 / 12</div>
    </div>

    <h1 class="title">Live Terminal: <span class="blue">Ultra-Clean Dark Bento UI</span></h1>
    <p class="subtitle">Designed for elite visual ergonomics, zero screen clutter, and instant cognitive clarity during high-volatility institutional market regimes.</p>

    <div class="grid-2" style="margin-top: 0.25in; align-items: center;">
      <div class="preview-box">
        <img src="{img_liquidity}" alt="Institutional Liquidity Terminal">
      </div>
      <div style="display: flex; flex-direction: column; gap: 16px;">
        <div class="bento-card highlight-blue">
          <div class="card-label">Hardware-Accelerated Overlay</div>
          <div class="card-title">Dotted Session Levels &amp; Sweeps</div>
          <p class="card-body">
            Clean institutional session boundaries: Asia High/Low (ASH/ASL), London High/Low (LSH/LSL), Previous Day High/Low (PDH/PDL), and Equal Highs/Lows (EQH/EQL). Dotted lines flash real-time &ldquo;⚡ Liquidity Swept&rdquo; badges when stop-hunts trigger.
          </p>
        </div>

        <div class="bento-card highlight-emerald">
          <div class="card-label">Single Crisp 1-Line Execution</div>
          <div class="card-title">Institutional Bento Signals Card</div>
          <p class="card-body">
            No messy multi-indicator cognitive overload. Delivers single crisp execution verdict: entry price, mathematical Take Profit, tight Stop Loss ($1.50 past wick), exact 1:3.0 Risk-Reward, and explicit stop-hunt absorption tags.
          </p>
        </div>
      </div>
    </div>

    <div class="slide-footer">
      <div>TradingPoint Technologies &bull; Techstars Pitch Deck</div>
      <div class="confidential">Live Production Web Terminal &bull; Verified in Chromium CDP Engine</div>
      <div>Slide 08 / 12</div>
    </div>
  </div>

  <!-- ===================================================================== -->
  <!-- SLIDE 9: MARKET SIZE: TAM / SAM / SOM                                -->
  <!-- ===================================================================== -->
  <div class="slide">
    <div class="slide-header">
      <div class="brand">
        <div class="logo-badge">TP</div>
        <div class="brand-title">TRADING<span>POINT</span> &bull; MARKET OPPORTUNITY</div>
      </div>
      <div class="slide-num">09 / 12</div>
    </div>

    <h1 class="title">Massive, Accelerating <span class="gold">Global Market</span></h1>
    <p class="subtitle">The explosion of retail prop trading firms and active CFD speculation creates unprecedented demand for autonomous institutional intelligence.</p>

    <div class="grid-3" style="margin-top: 0.35in;">
      <div class="bento-card highlight-gold">
        <div class="card-label">Total Addressable Market (TAM)</div>
        <div class="stat-hero gold">$11.8B</div>
        <div class="card-title">Global Retail Trading Tech</div>
        <p class="card-body">
          Combined global software spend by retail investors, algorithmic chart platforms, data APIs, and educational communities across equities, FX, crypto, and commodities.
        </p>
      </div>

      <div class="bento-card highlight-blue">
        <div class="card-label">Serviceable Available Market (SAM)</div>
        <div class="stat-hero blue">$2.9B</div>
        <div class="card-title">Active FX &amp; Metals Traders</div>
        <p class="card-body">
          Active retail day traders and prop firm candidates trading daily spot gold (XAU/USD), FX majors, and index CFDs who subscribe to third-party analytic software.
        </p>
      </div>

      <div class="bento-card highlight-emerald">
        <div class="card-label">Serviceable Obtainable Market (SOM)</div>
        <div class="stat-hero emerald">$180M</div>
        <div class="card-title">Systematic Prop Challenge Traders</div>
        <p class="card-body">
          Prop trading firm candidates (FTMO, FundedNext, SurgeTrader) seeking automated risk protection, drawdown defense, and SMC liquidity sweeps to pass evaluations.
        </p>
      </div>
    </div>

    <div class="slide-footer">
      <div>TradingPoint Technologies &bull; Techstars Pitch Deck</div>
      <div class="confidential">Market Sizing &bull; Bottom-Up Opportunity Analysis</div>
      <div>Slide 09 / 12</div>
    </div>
  </div>

  <!-- ===================================================================== -->
  <!-- SLIDE 10: BUSINESS MODEL & UNIT ECONOMICS                            -->
  <!-- ===================================================================== -->
  <div class="slide">
    <div class="slide-header">
      <div class="brand">
        <div class="logo-badge">TP</div>
        <div class="brand-title">TRADING<span>POINT</span> &bull; BUSINESS MODEL</div>
      </div>
      <div class="slide-num">10 / 12</div>
    </div>

    <h1 class="title">Scalable SaaS &amp; <span class="emerald">B2B API Monetization</span></h1>
    <p class="subtitle">High gross-margin recurring subscription revenue paired with high-volume enterprise API licensing for prop trading firms.</p>

    <div class="grid-2" style="margin-top: 0.3in;">
      <div class="bento-card">
        <div class="card-label">Recurring Revenue Tiers</div>
        <table class="fin-table">
          <thead>
            <tr>
              <th>Tier</th>
              <th>Price</th>
              <th>Target Audience</th>
              <th>Key Capabilities</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong style="color:#f1f5f9;">Free</strong></td>
              <td>$0</td>
              <td>Casual Traders</td>
              <td>Real-time spot feed, community access, delayed signals</td>
            </tr>
            <tr>
              <td><strong style="color:#34d399;">Pro Terminal</strong></td>
              <td>$39 / mo</td>
              <td>Active Day Traders</td>
              <td>Full SMC zones, 5-Tier MTF alignment, Liquidity Shield</td>
            </tr>
            <tr>
              <td><strong style="color:#38bdf8;">Institutional Quant</strong></td>
              <td>$129 / mo</td>
              <td>Prop Traders / Quants</td>
              <td>Webhook execution alerts, Sugra AI war radar, sub-15ms feeds</td>
            </tr>
            <tr>
              <td><strong style="color:#fbbf24;">Enterprise B2B</strong></td>
              <td>$499 / mo + vol</td>
              <td>Prop Trading Firms</td>
              <td>Prop firm risk engine, trader drawdown veto API, custom feeds</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="bento-card highlight-emerald">
        <div class="card-label">Venture-Grade Unit Economics</div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 15px;">
          <div>
            <div style="font-size: 12px; color: #94a3b8;">Customer Acq. Cost (CAC)</div>
            <div style="font-size: 32px; font-weight: 800; color: #f8fafc; font-family: 'JetBrains Mono';">$85</div>
          </div>
          <div>
            <div style="font-size: 12px; color: #94a3b8;">Lifetime Value (LTV)</div>
            <div style="font-size: 32px; font-weight: 800; color: #34d399; font-family: 'JetBrains Mono';">$620</div>
          </div>
          <div>
            <div style="font-size: 12px; color: #94a3b8;">LTV / CAC Ratio</div>
            <div style="font-size: 32px; font-weight: 800; color: #38bdf8; font-family: 'JetBrains Mono';">7.3x</div>
          </div>
          <div>
            <div style="font-size: 12px; color: #94a3b8;">Gross Margins</div>
            <div style="font-size: 32px; font-weight: 800; color: #fbbf24; font-family: 'JetBrains Mono';">88%</div>
          </div>
        </div>
        <p class="card-body" style="margin-top: 20px;">
          Viral community growth via transparent backtested performance records and prop firm challenge passing showcases. Payback period under 2.5 months.
        </p>
      </div>
    </div>

    <div class="slide-footer">
      <div>TradingPoint Technologies &bull; Techstars Pitch Deck</div>
      <div class="confidential">Unit Economics &bull; High Margin Serverless Architecture</div>
      <div>Slide 10 / 12</div>
    </div>
  </div>

  <!-- ===================================================================== -->
  <!-- SLIDE 11: COMPETITIVE ADVANTAGE & MOATS                              -->
  <!-- ===================================================================== -->
  <div class="slide">
    <div class="slide-header">
      <div class="brand">
        <div class="logo-badge">TP</div>
        <div class="brand-title">TRADING<span>POINT</span> &bull; COMPETITIVE ADVANTAGE</div>
      </div>
      <div class="slide-num">11 / 12</div>
    </div>

    <h1 class="title">Clear Competitive Moats &amp; <span class="blue">Differentiation</span></h1>
    <p class="subtitle">Unlike noisy charting canvases, TradingPoint is an autonomous execution decision engine engineered for institutional alignment.</p>

    <div style="margin-top: 0.25in;">
      <table class="fin-table">
        <thead>
          <tr>
            <th style="width: 25%;">Feature / Capability</th>
            <th style="color:#34d399; width: 18%;">TradingPoint</th>
            <th style="width: 14%;">TradingView</th>
            <th style="width: 14%;">MetaTrader 5</th>
            <th style="width: 14%;">TrendSpider</th>
            <th style="width: 15%;">Bloomberg Term.</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>Automated SMC Detection (FVG/OB)</strong></td>
            <td><span class="tag green">Native &bull; Zero Lag</span></td>
            <td>User scripts (noisy)</td>
            <td>Manual indicators</td>
            <td>Basic automation</td>
            <td>Manual order flow</td>
          </tr>
          <tr>
            <td><strong>Rule 0.1 Liquidity Shield</strong></td>
            <td><span class="tag green">Proprietary Veto</span></td>
            <td><span class="tag red">None</span></td>
            <td><span class="tag red">None</span></td>
            <td><span class="tag red">None</span></td>
            <td>Manual desk only</td>
          </tr>
          <tr>
            <td><strong>5-Tier Top-Down MTF Latch</strong></td>
            <td><span class="tag green">Built-In Matrix</span></td>
            <td>Separate windows</td>
            <td>Separate charts</td>
            <td>Multi-timeframe view</td>
            <td>Multi-screen setup</td>
          </tr>
          <tr>
            <td><strong>Macro Geopolitical War Radar</strong></td>
            <td><span class="tag green">Sugra AI Stream</span></td>
            <td><span class="tag red">None</span></td>
            <td><span class="tag red">None</span></td>
            <td>News headline feed</td>
            <td>News terminal ($25K)</td>
          </tr>
          <tr>
            <td><strong>Annual Cost to User</strong></td>
            <td><span class="tag green"><strong>$468 / yr</strong></span></td>
            <td>$180 - $720 / yr</td>
            <td>Free (Broker locked)</td>
            <td>$900 - $1,500 / yr</td>
            <td><strong>$25,000+ / yr</strong></td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="slide-footer">
      <div>TradingPoint Technologies &bull; Techstars Pitch Deck</div>
      <div class="confidential">Competitive Analysis &bull; Defensible Algorithmic Edge</div>
      <div>Slide 11 / 12</div>
    </div>
  </div>

  <!-- ===================================================================== -->
  <!-- SLIDE 12: FOUNDER & TECHSTARS 12-MONTH MILESTONES                     -->
  <!-- ===================================================================== -->
  <div class="slide">
    <div class="slide-header">
      <div class="brand">
        <div class="logo-badge">TP</div>
        <div class="brand-title">TRADING<span>POINT</span> &bull; FOUNDER &amp; TECHSTARS ASK</div>
      </div>
      <div class="slide-num">12 / 12</div>
    </div>

    <h1 class="title">Founder &amp; <span class="emerald">Techstars Milestones</span></h1>
    <p class="subtitle">Proven execution velocity, deep technical craftsmanship, and a clear path to $2.1M ARR within 12 months of accelerator acceleration.</p>

    <div class="grid-2" style="margin-top: 0.3in;">
      <div class="bento-card highlight-blue">
        <div class="card-label">Solo Founder &amp; Architect</div>
        <div class="card-title">Suneel Pirkash</div>
        <p class="card-body" style="font-size: 15px; line-height: 1.6;">
          Full-stack software engineer and quantitative trading systems architect. Deep domain mastery in financial market microstructure, high-concurrency real-time WebSocket pipelines, and institutional Smart Money Concepts. Built and shipped the entire TradingPoint terminal end-to-end with verified empirical backtesting rigor.
        </p>
        <div style="margin-top: 20px; display: flex; gap: 10px;">
          <span class="tag blue">Full-Stack Engineer</span>
          <span class="tag green">Quantitative Systems</span>
          <span class="tag gold">Market Microstructure</span>
        </div>
      </div>

      <div class="bento-card highlight-emerald">
        <div class="card-label">Techstars Accelerator Ask &amp; Runway</div>
        <div class="card-title">$120,000 &ndash; $250,000 Investment</div>
        
        <div style="margin-top: 15px; display: flex; flex-direction: column; gap: 12px; font-size: 13.5px; color: #cbd5e1;">
          <div>
            <strong style="color:#38bdf8;">Month 1 - 3:</strong> Public Pro Beta Launch &bull; 500 Paid Subscribers ($19.5K MRR).
          </div>
          <div>
            <strong style="color:#34d399;">Month 4 - 6:</strong> Sign first 3 Prop Firm B2B Risk API pilot contracts &bull; 1,500 Subscribers ($58K MRR).
          </div>
          <div>
            <strong style="color:#fbbf24;">Month 7 - 9:</strong> Multi-Asset Expansion (Bitcoin, Crude Oil, S&amp;P 500) &bull; Native Mobile App Launch.
          </div>
          <div>
            <strong style="color:#a78bfa;">Month 10 - 12:</strong> Scale to <strong>5,000 Paid Subscribers ($180K MRR / $2.1M ARR)</strong> at 85%+ gross margin.
          </div>
        </div>
      </div>
    </div>

    <div class="slide-footer">
      <div>TradingPoint Technologies &bull; Techstars Pitch Deck</div>
      <div class="confidential">Founder Profile &bull; 12-Month Accelerator Execution Roadmap</div>
      <div>Slide 12 / 12</div>
    </div>
  </div>

</body>
</html>
"""

    html_path = os.path.abspath("TradingPoint_Techstars_Pitch_Deck.html")
    pdf_path = os.path.abspath("TradingPoint_Techstars_Pitch_Deck.pdf")

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Saved HTML presentation to {html_path} ({len(html_content):,} bytes)")

    print("Compiling pixel-perfect PDF via Edge Headless...")
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    cmd = [
        edge_path,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path}",
        html_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if os.path.exists(pdf_path):
        size = os.path.getsize(pdf_path)
        print(f"\n[SUCCESS] PDF successfully created: {pdf_path}")
        print(f"File size: {size:,} bytes ({size / (1024*1024):.2f} MB)")
        return pdf_path
    else:
        print("[ERROR] PDF generation failed!")
        return None

if __name__ == '__main__':
    generate_pitch_deck()
