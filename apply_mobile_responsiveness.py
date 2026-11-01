"""
Apply complete TradingView & Exness mobile responsiveness to gold_dashboard.html, index.html, deep_analysis_gold.html.
"""

import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

# 1. New Viewport Meta Tag
OLD_VIEWPORT = '<meta name="viewport" content="width=device-width, initial-scale=1.0" />'
NEW_VIEWPORT = '<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover" />'

# 2. Mobile Pill Row HTML in Subheader
TARGET_SUBHEADER = """        <!-- Symbol Pill -->
        <div class="tv-symbol-pill">
          <span class="tv-sym-title">XAU/USD</span>
          <span class="tv-sym-dot"></span>
        </div>"""

REPLACEMENT_SUBHEADER = """        <!-- Symbol Pill -->
        <div class="tv-symbol-pill">
          <span class="tv-sym-title">XAU/USD</span>
          <span class="tv-sym-dot"></span>
          <span id="mobileTopSpotPrice" class="mobile-top-spot-price" style="display: none;">$4,007.05</span>
        </div>

        <!-- Mobile Horizontally Scrollable Timeframe Pill Row (TradingView / Exness Style) -->
        <div class="mobile-tf-pill-row" id="mobileTfPillRow">
          <button type="button" class="mobile-tf-pill" data-tf="1m" onclick="selectTimeframe('1m')">1m</button>
          <button type="button" class="mobile-tf-pill" data-tf="5m" onclick="selectTimeframe('5m')">5m</button>
          <button type="button" class="mobile-tf-pill active" data-tf="15m" onclick="selectTimeframe('15m')">15m</button>
          <button type="button" class="mobile-tf-pill" data-tf="1h" onclick="selectTimeframe('1h')">1H</button>
          <button type="button" class="mobile-tf-pill" data-tf="4h" onclick="selectTimeframe('4h')">4H</button>
          <button type="button" class="mobile-tf-pill" data-tf="1d" onclick="selectTimeframe('1d')">1D</button>
          <button type="button" class="mobile-tf-pill" data-tf="1w" onclick="selectTimeframe('1w')">1W</button>
        </div>"""

# 3. Mobile Bottom Nav & Slide-Up Bottom Sheets Markup
TARGET_BOTTOM_TERMINAL = """    </div>
  </div>


  <!-- ========================================================
       TRADINGVIEW-GRADE INTERACTIVE TOOLBAR MODALS"""

REPLACEMENT_BOTTOM_TERMINAL = """    </div>

    <!-- ========================================================
         TRADINGVIEW / EXNESS STYLE MOBILE BOTTOM NAVIGATION DOCK
         ======================================================== -->
    <nav id="mobileBottomNav" class="mobile-bottom-nav" aria-label="Mobile Trading Navigation">
      <button type="button" class="mobile-nav-tab active" data-tab="chart" onclick="switchMobileTab('chart')">
        <span class="m-nav-icon">📈</span>
        <span class="m-nav-label">Chart</span>
      </button>
      <button type="button" class="mobile-nav-tab" data-tab="execution" onclick="switchMobileTab('execution')">
        <span class="m-nav-icon">⚡</span>
        <span class="m-nav-label">Trade</span>
      </button>
      <button type="button" class="mobile-nav-tab" data-tab="signals" onclick="switchMobileTab('signals')">
        <span class="m-nav-icon">🎯</span>
        <span class="m-nav-label">Signals</span>
      </button>
      <button type="button" class="mobile-nav-tab" data-tab="wallet" onclick="switchMobileTab('wallet')">
        <span class="m-nav-icon">💼</span>
        <span class="m-nav-label">Wallet</span>
        <span id="mNavPosBadge" class="m-nav-badge" style="display: none;">0</span>
      </button>
    </nav>

    <!-- Semi-Transparent Mobile Sheet Backdrop -->
    <div id="mobileSheetBackdrop" class="mobile-sheet-backdrop" onclick="switchMobileTab('chart')"></div>

    <!-- Mobile Slide-Up Modal Bottom Sheet Container -->
    <div id="mobileSheetContainer" class="mobile-sheet-container" role="dialog" aria-modal="true">
      <div class="mobile-sheet-header">
        <div class="mobile-sheet-grab-bar" onclick="switchMobileTab('chart')"></div>
        <div class="mobile-sheet-title-row">
          <div style="display: flex; align-items: center; gap: 8px;">
            <span id="mobileSheetTitleIcon">⚡</span>
            <span id="mobileSheetTitle" class="mobile-sheet-title-text">Execution Pad</span>
          </div>
          <button type="button" class="mobile-sheet-close-btn" onclick="switchMobileTab('chart')" aria-label="Close Sheet">✕</button>
        </div>
      </div>

      <div class="mobile-sheet-content" id="mobileSheetContent">
        <!-- 1. EXECUTION / BUY-SELL PANEL -->
        <div id="mPanelExecution" class="mobile-sheet-panel">
          <!-- Spot Quote & Spread Strip -->
          <div class="m-quote-strip">
            <div style="display: flex; align-items: center; gap: 8px;">
              <span class="m-asset-badge">XAU/USD SPOT</span>
              <span id="mLiveSpotPrice" class="m-live-spot">$4,007.05</span>
            </div>
            <div class="m-spread-badge">Spread: <strong style="color: #3fb950;">~0.15 pts</strong></div>
          </div>

          <!-- Account Equity Bar -->
          <div class="m-account-bar">
            <div>
              <span class="m-acc-lbl">EQUITY</span>
              <span id="mAccountEquity" class="m-acc-val">$1,000.00</span>
            </div>
            <div>
              <span class="m-acc-lbl">FREE MARGIN</span>
              <span id="mAccountFreeMargin" class="m-acc-val" style="color: #58a6ff;">$1,000.00</span>
            </div>
            <div>
              <span class="m-acc-lbl">FLOATING PNL</span>
              <span id="mAccountFloatingPnl" class="m-acc-val" style="color: #8b949e;">$0.00</span>
            </div>
          </div>

          <!-- Lot Size Selector (Fat-Finger Touch Targets >= 44px) -->
          <div class="m-lot-section">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
              <label class="m-field-lbl">LOT SIZE (0.01 - 5.00 L):</label>
              <span id="mLotMarginCalc" style="font-size: 11px; color: #ffd700; font-weight: 600;">Margin: ~$40</span>
            </div>
            <div class="m-lot-input-grid">
              <button type="button" class="m-touch-btn m-lot-step-btn" onclick="stepMobileLot(-0.01)" aria-label="Decrease lot size">-</button>
              <input type="number" id="mDemoLotInput" class="m-lot-input" value="0.01" min="0.01" max="5.00" step="0.01" onchange="syncMobileLot(this.value)">
              <button type="button" class="m-touch-btn m-lot-step-btn" onclick="stepMobileLot(0.01)" aria-label="Increase lot size">+</button>
            </div>
            <div class="m-lot-quick-pills">
              <button type="button" class="m-lot-pill active" onclick="setMobileLot(0.01)">0.01</button>
              <button type="button" class="m-lot-pill" onclick="setMobileLot(0.02)">0.02</button>
              <button type="button" class="m-lot-pill" onclick="setMobileLot(0.05)">0.05</button>
              <button type="button" class="m-lot-pill" onclick="setMobileLot(0.10)">0.10</button>
              <button type="button" class="m-lot-pill" onclick="setMobileLot(0.50)">0.50</button>
              <button type="button" class="m-lot-pill" onclick="setMobileLot(1.00)">1.00</button>
            </div>
          </div>

          <!-- SL / TP Target Inputs (Min 44px Touch Targets) -->
          <div class="m-targets-grid">
            <div>
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                <label class="m-field-lbl" style="color: #f85149;">STOP LOSS (SL)</label>
                <button type="button" class="m-quick-offset-btn" onclick="setMobileTargetOffset('sl')">- $2.50 Auto</button>
              </div>
              <input type="number" id="mDemoSlInput" class="m-target-input m-sl-input" placeholder="Auto / None" step="0.5" onchange="syncMobileTarget('sl', this.value)">
            </div>
            <div>
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                <label class="m-field-lbl" style="color: #3fb950;">TAKE PROFIT (TP)</label>
                <button type="button" class="m-quick-offset-btn" onclick="setMobileTargetOffset('tp')">+ $12.00 (1:3)</button>
              </div>
              <input type="number" id="mDemoTpInput" class="m-target-input m-tp-input" placeholder="Auto / None" step="0.5" onchange="syncMobileTarget('tp', this.value)">
            </div>
          </div>

          <!-- Big Exness / TradingView Style Buy & Sell Buttons (Min 52px Touch Target) -->
          <div class="m-exec-buttons-grid">
            <button type="button" class="m-touch-btn m-btn-sell" onclick="executeMobileOrder('SELL')">
              <div class="m-exec-head">▼ SELL / SHORT</div>
              <div class="m-exec-price" id="mSellTickerPrice">$4,007.05</div>
            </button>
            <button type="button" class="m-touch-btn m-btn-buy" onclick="executeMobileOrder('BUY')">
              <div class="m-exec-head">▲ BUY / LONG</div>
              <div class="m-exec-price" id="mBuyTickerPrice">$4,007.05</div>
            </button>
          </div>
        </div>

        <!-- 2. SIGNALS & SMC RADAR PANEL -->
        <div id="mPanelSignals" class="mobile-sheet-panel" style="display: none;">
          <div id="mSignalsContainer" class="m-signals-wrapper">
            <!-- Populated dynamically from executionSignalsCard & twelveSugraRadarCard -->
          </div>
        </div>

        <!-- 3. DEMO WALLET & POSITIONS PANEL -->
        <div id="mPanelWallet" class="mobile-sheet-panel" style="display: none;">
          <!-- Wallet KPI Cards -->
          <div class="m-wallet-kpi-grid">
            <div class="m-wallet-box">
              <span class="dw-label">BALANCE</span>
              <span class="dw-val" id="mWalletBalance">$1,000.00</span>
            </div>
            <div class="m-wallet-box">
              <span class="dw-label">DYNAMIC EQUITY</span>
              <span class="dw-val" id="mWalletEquity">$1,000.00</span>
            </div>
            <div class="m-wallet-box">
              <span class="dw-label">FLOATING PNL</span>
              <span class="dw-val" id="mWalletPnl" style="color: #8b949e;">$0.00</span>
            </div>
            <div class="m-wallet-box">
              <span class="dw-label">FREE MARGIN</span>
              <span class="dw-val" id="mWalletFreeMargin">$1,000.00</span>
            </div>
          </div>

          <!-- Open Positions Header & Close All -->
          <div class="m-pos-header">
            <span style="font-weight: 700; font-size: 13px; color: #f0f6fc;">OPEN POSITIONS (<span id="mWalletPosCount">0</span>)</span>
            <button type="button" class="btn-close-all" id="mBtnCloseAll" onclick="closeAllDemoPositions()" style="display: none;">Close All</button>
          </div>

          <!-- Positions List -->
          <div id="mPositionsList" class="demo-pos-list" style="margin-top: 8px;">
            <div class="demo-empty-placeholder">No active demo positions. Tap 'Trade' tab to open an order.</div>
          </div>
        </div>
      </div>
    </div>
  </div>


  <!-- ========================================================
       TRADINGVIEW-GRADE INTERACTIVE TOOLBAR MODALS"""

# 4. Mobile Responsive CSS Injection
MOBILE_RESPONSIVE_CSS = """
    /* ========================================================
       TRADINGVIEW & EXNESS INSPIRED 100% MOBILE RESPONSIVE ENGINE
       ======================================================== */
    @media (max-width: 768px) {
      html, body {
        width: 100% !important;
        height: 100% !important;
        height: 100dvh !important;
        overflow-x: hidden !important;
        position: relative !important;
        -webkit-tap-highlight-color: transparent !important;
      }

      /* Single Viewport Full-Height Container */
      #view-terminal {
        width: 100% !important;
        height: 100vh !important;
        height: 100dvh !important;
        max-height: 100dvh !important;
        overflow: hidden !important;
        display: flex !important;
        flex-direction: column !important;
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        bottom: 0 !important;
        z-index: 100 !important;
        margin: 0 !important;
        padding: 0 !important;
        background: #0d1117 !important;
      }

      /* Sleek Mobile Subheader & Timeframe Pill Bar */
      .terminal-sub-header {
        height: 48px !important;
        min-height: 48px !important;
        padding: 0 10px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        background: #11151c !important;
        border-bottom: 1px solid #21262d !important;
        flex-shrink: 0 !important;
        overflow-x: auto !important;
        overflow-y: hidden !important;
        white-space: nowrap !important;
        scrollbar-width: none !important;
        -webkit-overflow-scrolling: touch !important;
        padding-top: env(safe-area-inset-top) !important;
      }
      .terminal-sub-header::-webkit-scrollbar {
        display: none !important;
      }

      .mobile-top-spot-price {
        display: inline-block !important;
        color: #ffd700 !important;
        font-weight: 800 !important;
        font-family: 'Space Grotesk', monospace !important;
        font-size: 13px !important;
        margin-left: 6px !important;
      }

      /* Hide Desktop Clutter in Mobile Subheader */
      #tvTimeframeContainer,
      #tvCandleContainer,
      #tvIndicatorsContainer,
      .terminal-sub-header > .terminal-nav-left > span[style*="color: #30363d;"],
      #smcThemeToggleBtn,
      #btn-fit,
      #soundToggleBtn {
        display: none !important;
      }

      /* Horizontally Scrollable Timeframe Pills */
      .mobile-tf-pill-row {
        display: flex !important;
        align-items: center !important;
        gap: 6px !important;
        margin-left: 6px !important;
        overflow-x: auto !important;
        white-space: nowrap !important;
        scrollbar-width: none !important;
        -webkit-overflow-scrolling: touch !important;
      }
      .mobile-tf-pill-row::-webkit-scrollbar {
        display: none !important;
      }
      .mobile-tf-pill {
        min-height: 38px !important;
        min-width: 44px !important;
        padding: 0 10px !important;
        border-radius: 8px !important;
        border: 1px solid #30363d !important;
        background: #161b22 !important;
        color: #8b949e !important;
        font-size: 12.5px !important;
        font-weight: 700 !important;
        font-family: inherit !important;
        cursor: pointer !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        user-select: none !important;
        touch-action: manipulation !important;
      }
      .mobile-tf-pill.active {
        background: #238636 !important;
        color: #ffffff !important;
        border-color: #2ea043 !important;
        box-shadow: 0 0 8px rgba(46, 160, 67, 0.4) !important;
      }

      /* Full Screen Chart First Architecture */
      .terminal-body {
        flex: 1 !important;
        height: auto !important;
        min-height: 0 !important;
        width: 100% !important;
        position: relative !important;
        display: flex !important;
        flex-direction: column !important;
        overflow: hidden !important;
        margin-bottom: calc(56px + env(safe-area-inset-bottom)) !important;
      }
      .terminal-chart-pane {
        flex: 1 !important;
        width: 100% !important;
        height: 100% !important;
        min-height: 0 !important;
        position: relative !important;
        display: flex !important;
        flex-direction: column !important;
      }
      #chart {
        flex: 1 !important;
        width: 100% !important;
        height: 100% !important;
        min-height: 0 !important;
      }

      /* Hide desktop sidebar, left toolbar, and watermarks */
      .terminal-sidebar {
        display: none !important;
      }
      .tv-left-toolbar {
        display: none !important;
      }
      .navbar {
        display: none !important;
      }
      #macroNewsAlertBanner {
        display: none !important;
      }
      .smc-session-watermark {
        display: none !important;
      }

      /* Fixed Bottom Navigation Dock */
      .mobile-bottom-nav {
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        right: 0 !important;
        height: calc(56px + env(safe-area-inset-bottom)) !important;
        background: rgba(13, 17, 23, 0.96) !important;
        backdrop-filter: blur(14px) !important;
        -webkit-backdrop-filter: blur(14px) !important;
        border-top: 1px solid rgba(48, 54, 61, 0.9) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: space-around !important;
        padding-bottom: env(safe-area-inset-bottom) !important;
        z-index: 10000 !important;
        box-sizing: border-box !important;
      }
      .mobile-nav-tab {
        flex: 1 !important;
        height: 100% !important;
        min-height: 48px !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 3px !important;
        background: transparent !important;
        border: none !important;
        color: #8b949e !important;
        cursor: pointer !important;
        user-select: none !important;
        touch-action: manipulation !important;
        position: relative !important;
        padding: 4px 0 !important;
      }
      .mobile-nav-tab.active {
        color: #ffd700 !important;
      }
      .mobile-nav-tab.active .m-nav-label {
        color: #ffd700 !important;
        font-weight: 700 !important;
      }
      .m-nav-icon {
        font-size: 19px !important;
        line-height: 1 !important;
      }
      .m-nav-label {
        font-size: 10.5px !important;
        font-weight: 600 !important;
        letter-spacing: 0.2px !important;
        font-family: 'Space Grotesk', -apple-system, sans-serif !important;
      }
      .m-nav-badge {
        position: absolute !important;
        top: 4px !important;
        right: 22% !important;
        background: #f85149 !important;
        color: #ffffff !important;
        font-size: 9px !important;
        font-weight: 800 !important;
        padding: 1px 5px !important;
        border-radius: 10px !important;
        border: 1px solid #0d1117 !important;
      }

      /* Slide-Up Bottom Sheet Modal */
      .mobile-sheet-backdrop {
        position: fixed !important;
        inset: 0 !important;
        background: rgba(0, 0, 0, 0.65) !important;
        backdrop-filter: blur(4px) !important;
        -webkit-backdrop-filter: blur(4px) !important;
        z-index: 9998 !important;
        opacity: 0 !important;
        pointer-events: none !important;
        transition: opacity 0.25s ease !important;
      }
      .mobile-sheet-backdrop.active {
        opacity: 1 !important;
        pointer-events: auto !important;
      }

      .mobile-sheet-container {
        position: fixed !important;
        left: 0 !important;
        right: 0 !important;
        bottom: calc(56px + env(safe-area-inset-bottom)) !important;
        max-height: 82vh !important;
        max-height: 82dvh !important;
        background: #161b22 !important;
        border-top: 1px solid #30363d !important;
        border-radius: 16px 16px 0 0 !important;
        z-index: 9999 !important;
        transform: translateY(105%) !important;
        transition: transform 0.28s cubic-bezier(0.16, 1, 0.3, 1) !important;
        display: flex !important;
        flex-direction: column !important;
        overflow: hidden !important;
        box-shadow: 0 -12px 35px rgba(0, 0, 0, 0.75) !important;
      }
      .mobile-sheet-container.active {
        transform: translateY(0) !important;
      }

      .mobile-sheet-header {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        padding: 8px 16px 6px !important;
        border-bottom: 1px solid #21262d !important;
        background: #161b22 !important;
        flex-shrink: 0 !important;
      }
      .mobile-sheet-grab-bar {
        width: 36px !important;
        height: 4px !important;
        background: #484f58 !important;
        border-radius: 2px !important;
        margin-bottom: 8px !important;
        cursor: pointer !important;
      }
      .mobile-sheet-title-row {
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        width: 100% !important;
      }
      .mobile-sheet-title-text {
        font-weight: 700 !important;
        font-size: 13.5px !important;
        color: #f0f6fc !important;
        letter-spacing: 0.3px !important;
      }
      .mobile-sheet-close-btn {
        width: 30px !important;
        height: 30px !important;
        border-radius: 50% !important;
        background: #21262d !important;
        border: 1px solid #30363d !important;
        color: #c9d1d9 !important;
        font-size: 13px !important;
        cursor: pointer !important;
        display: grid !important;
        place-items: center !important;
        line-height: 1 !important;
      }

      .mobile-sheet-content {
        overflow-y: auto !important;
        -webkit-overflow-scrolling: touch !important;
        padding: 14px 14px calc(14px + env(safe-area-inset-bottom)) !important;
        flex: 1 !important;
      }

      /* Execution Pad Styling */
      .m-quote-strip {
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        background: #0d1117 !important;
        border: 1px solid #21262d !important;
        border-radius: 8px !important;
        padding: 10px 12px !important;
        margin-bottom: 12px !important;
      }
      .m-asset-badge {
        font-weight: 800 !important;
        font-size: 11px !important;
        letter-spacing: 0.5px !important;
        background: rgba(255, 215, 0, 0.15) !important;
        color: #ffd700 !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
        border: 1px solid rgba(255, 215, 0, 0.3) !important;
      }
      .m-live-spot {
        font-size: 16px !important;
        font-weight: 800 !important;
        font-family: 'Space Grotesk', monospace !important;
        color: #f0f6fc !important;
      }
      .m-spread-badge {
        font-size: 11px !important;
        color: #8b949e !important;
      }

      .m-account-bar {
        display: grid !important;
        grid-template-columns: 1fr 1fr 1fr !important;
        gap: 8px !important;
        background: #0d1117 !important;
        border: 1px solid #21262d !important;
        border-radius: 8px !important;
        padding: 8px 10px !important;
        margin-bottom: 12px !important;
        text-align: center !important;
      }
      .m-acc-lbl {
        font-size: 9px !important;
        font-weight: 700 !important;
        color: #8b949e !important;
        display: block !important;
        letter-spacing: 0.5px !important;
        margin-bottom: 2px !important;
      }
      .m-acc-val {
        font-size: 12px !important;
        font-weight: 800 !important;
        font-family: 'Space Grotesk', monospace !important;
        color: #f0f6fc !important;
      }

      /* Lot Selector Grid */
      .m-lot-section {
        background: #0d1117 !important;
        border: 1px solid #21262d !important;
        border-radius: 8px !important;
        padding: 10px 12px !important;
        margin-bottom: 12px !important;
      }
      .m-field-lbl {
        font-size: 10px !important;
        font-weight: 700 !important;
        color: #8b949e !important;
        letter-spacing: 0.5px !important;
      }
      .m-lot-input-grid {
        display: grid !important;
        grid-template-columns: 50px 1fr 50px !important;
        gap: 8px !important;
        margin: 8px 0 !important;
      }
      .m-touch-btn {
        min-height: 44px !important;
        border-radius: 8px !important;
        cursor: pointer !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        user-select: none !important;
        touch-action: manipulation !important;
      }
      .m-lot-step-btn {
        background: #21262d !important;
        border: 1px solid #30363d !important;
        color: #f0f6fc !important;
        font-size: 20px !important;
        font-weight: 700 !important;
      }
      .m-lot-step-btn:active {
        background: #30363d !important;
      }
      .m-lot-input {
        min-height: 44px !important;
        background: #161b22 !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
        color: #f0f6fc !important;
        font-size: 17px !important;
        font-weight: 800 !important;
        text-align: center !important;
        font-family: 'Space Grotesk', monospace !important;
        outline: none !important;
        box-sizing: border-box !important;
      }
      .m-lot-quick-pills {
        display: grid !important;
        grid-template-columns: repeat(6, 1fr) !important;
        gap: 5px !important;
        margin-top: 6px !important;
      }
      .m-lot-pill {
        min-height: 38px !important;
        background: #161b22 !important;
        border: 1px solid #30363d !important;
        border-radius: 6px !important;
        color: #8b949e !important;
        font-size: 12px !important;
        font-weight: 700 !important;
        cursor: pointer !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        touch-action: manipulation !important;
      }
      .m-lot-pill.active {
        background: #1f6feb !important;
        border-color: #388bfd !important;
        color: #ffffff !important;
      }

      /* Targets Grid */
      .m-targets-grid {
        display: grid !important;
        grid-template-columns: 1fr 1fr !important;
        gap: 8px !important;
        margin-bottom: 14px !important;
      }
      .m-quick-offset-btn {
        background: transparent !important;
        border: none !important;
        color: #58a6ff !important;
        font-size: 10px !important;
        font-weight: 600 !important;
        cursor: pointer !important;
        padding: 0 !important;
      }
      .m-target-input {
        width: 100% !important;
        min-height: 44px !important;
        background: #0d1117 !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
        padding: 0 10px !important;
        font-size: 13px !important;
        font-weight: 700 !important;
        font-family: 'Space Grotesk', monospace !important;
        outline: none !important;
        box-sizing: border-box !important;
      }
      .m-sl-input {
        color: #f85149 !important;
        border-color: rgba(248, 81, 73, 0.4) !important;
      }
      .m-tp-input {
        color: #3fb950 !important;
        border-color: rgba(63, 185, 80, 0.4) !important;
      }

      /* Big Execution Buttons */
      .m-exec-buttons-grid {
        display: grid !important;
        grid-template-columns: 1fr 1fr !important;
        gap: 10px !important;
        margin-top: 6px !important;
      }
      .m-btn-sell {
        min-height: 52px !important;
        background: #da3633 !important;
        border: 1px solid #f85149 !important;
        border-radius: 10px !important;
        color: #ffffff !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 4px 12px rgba(218, 54, 51, 0.35) !important;
      }
      .m-btn-sell:active {
        background: #b62324 !important;
      }
      .m-btn-buy {
        min-height: 52px !important;
        background: #238636 !important;
        border: 1px solid #2ea043 !important;
        border-radius: 10px !important;
        color: #ffffff !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 4px 12px rgba(35, 134, 54, 0.35) !important;
      }
      .m-btn-buy:active {
        background: #1b6528 !important;
      }
      .m-exec-head {
        font-size: 13px !important;
        font-weight: 800 !important;
        letter-spacing: 0.5px !important;
      }
      .m-exec-price {
        font-size: 14px !important;
        font-weight: 800 !important;
        font-family: 'Space Grotesk', monospace !important;
        opacity: 0.95 !important;
      }

      /* Wallet Panel */
      .m-wallet-kpi-grid {
        display: grid !important;
        grid-template-columns: 1fr 1fr !important;
        gap: 8px !important;
        margin-bottom: 14px !important;
      }
      .m-wallet-box {
        background: #0d1117 !important;
        border: 1px solid #21262d !important;
        border-radius: 8px !important;
        padding: 10px !important;
      }
      .m-pos-header {
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        padding-bottom: 6px !important;
        border-bottom: 1px solid #21262d !important;
      }

      /* Touch-Friendly Dialogs */
      .tv-modal,
      .auth-modal-card {
        width: 92% !important;
        max-width: 380px !important;
        margin: auto !important;
        box-sizing: border-box !important;
        border-radius: 14px !important;
      }

      /* Responsive Landing Page Elements */
      .showcase-hero {
        padding: 16px 12px !important;
      }
      .indicator-grid,
      .driver-grid,
      .research-grid,
      .bottom-grid,
      .faq-grid,
      .footer-grid {
        grid-template-columns: 1fr !important;
        gap: 12px !important;
      }
      .comparison-table-wrapper {
        overflow-x: auto !important;
        -webkit-overflow-scrolling: touch !important;
      }
    }
"""

# 5. Lightweight Charts Touch Handling Options
TARGET_CHART_OPTIONS = """      handleScroll: {
        mouseWheel: true,
        pressedMouseMove: true,
        horzTouchDrag: true,
        vertTouchDrag: false,
      },
      handleScale: {
        axisPressedMouseMove: {
          time: true,
          price: false,
        },
        axisDoubleClickReset: true,
        mouseWheel: true,
        pinch: true,
      },"""

REPLACEMENT_CHART_OPTIONS = """      handleScroll: {
        mouseWheel: true,
        pressedMouseMove: true,
        horzTouchDrag: true,
        vertTouchDrag: true,
      },
      handleScale: {
        axisPressedMouseMove: {
          time: true,
          price: true,
        },
        axisDoubleClickReset: true,
        mouseWheel: true,
        pinch: true,
      },
      kineticScroll: {
        touch: true,
        mouse: false,
      },"""

# 6. JavaScript Mobile Handlers & Logic
MOBILE_JS_HANDLERS = """
    // ========================================================
    // TRADINGVIEW & EXNESS INSPIRED MOBILE NAVIGATION ENGINE
    // ========================================================
    let currentMobileTab = 'chart';

    function switchMobileTab(tab) {
      currentMobileTab = tab;
      const backdrop = document.getElementById('mobileSheetBackdrop');
      const container = document.getElementById('mobileSheetContainer');
      const panelExec = document.getElementById('mPanelExecution');
      const panelSig = document.getElementById('mPanelSignals');
      const panelWal = document.getElementById('mPanelWallet');
      const titleEl = document.getElementById('mobileSheetTitle');
      const iconEl = document.getElementById('mobileSheetTitleIcon');

      // Update active state on bottom dock tabs
      document.querySelectorAll('.mobile-nav-tab').forEach(btn => {
        btn.classList.toggle('active', btn.getAttribute('data-tab') === tab);
      });

      if (tab === 'chart') {
        if (backdrop) backdrop.classList.remove('active');
        if (container) container.classList.remove('active');
        setTimeout(() => {
          if (panelExec) panelExec.style.display = 'none';
          if (panelSig) panelSig.style.display = 'none';
          if (panelWal) panelWal.style.display = 'none';
          if (window.chart && typeof window.chart.resize === 'function') {
            const c = document.getElementById('chart');
            if (c) window.chart.resize(c.clientWidth, c.clientHeight);
          }
          if (typeof syncCanvasSize === 'function') syncCanvasSize();
        }, 220);
        return;
      }

      // Show bottom sheet
      if (panelExec) panelExec.style.display = (tab === 'execution' ? 'block' : 'none');
      if (panelSig) panelSig.style.display = (tab === 'signals' ? 'block' : 'none');
      if (panelWal) panelWal.style.display = (tab === 'wallet' ? 'block' : 'none');

      if (titleEl) {
        if (tab === 'execution') {
          titleEl.innerText = 'Quick Execution Pad';
          if (iconEl) iconEl.innerText = '⚡';
        } else if (tab === 'signals') {
          titleEl.innerText = 'Execution Signals & SMC Radar';
          if (iconEl) iconEl.innerText = '🎯';
        } else if (tab === 'wallet') {
          titleEl.innerText = 'Virtual Demo Wallet & Positions';
          if (iconEl) iconEl.innerText = '💼';
        }
      }

      if (backdrop) backdrop.classList.add('active');
      if (container) container.classList.add('active');

      if (tab === 'execution') {
        updateMobileExecutionValues();
      } else if (tab === 'signals') {
        renderMobileSignalsContent();
      } else if (tab === 'wallet') {
        renderMobileWalletUI();
      }
    }

    function syncMobileLot(val) {
      const num = parseFloat(val) || 0.01;
      const desktopLot = document.getElementById('demoLotInput');
      if (desktopLot) desktopLot.value = num.toFixed(2);
      if (typeof setLotSize === 'function') setLotSize(num);
      updateMobileExecutionValues();
    }

    function stepMobileLot(delta) {
      const mInput = document.getElementById('mDemoLotInput');
      let cur = parseFloat(mInput ? mInput.value : 0.01) || 0.01;
      cur = Math.max(0.01, Math.min(5.00, parseFloat((cur + delta).toFixed(2))));
      if (mInput) mInput.value = cur.toFixed(2);
      syncMobileLot(cur);
    }

    function setMobileLot(val) {
      const mInput = document.getElementById('mDemoLotInput');
      if (mInput) mInput.value = val.toFixed(2);
      document.querySelectorAll('.m-lot-pill').forEach(pill => {
        pill.classList.toggle('active', Math.abs(parseFloat(pill.innerText) - val) < 0.001);
      });
      syncMobileLot(val);
    }

    function syncMobileTarget(targetType, val) {
      if (targetType === 'sl') {
        const desktopSl = document.getElementById('demoSlInput');
        if (desktopSl) desktopSl.value = val;
      } else {
        const desktopTp = document.getElementById('demoTpInput');
        if (desktopTp) desktopTp.value = val;
      }
    }

    function setMobileTargetOffset(targetType) {
      const price = typeof currentLiveSpot !== 'undefined' ? currentLiveSpot : 4007.05;
      if (targetType === 'sl') {
        const slVal = Number((price - 2.50).toFixed(2));
        const inp = document.getElementById('mDemoSlInput');
        if (inp) inp.value = slVal;
        syncMobileTarget('sl', slVal);
      } else {
        const tpVal = Number((price + 12.00).toFixed(2));
        const inp = document.getElementById('mDemoTpInput');
        if (inp) inp.value = tpVal;
        syncMobileTarget('tp', tpVal);
      }
    }

    function executeMobileOrder(type) {
      // Sync lot and targets to desktop inputs
      const mLot = document.getElementById('mDemoLotInput');
      const mSl = document.getElementById('mDemoSlInput');
      const mTp = document.getElementById('mDemoTpInput');

      const dLot = document.getElementById('demoLotInput');
      const dSl = document.getElementById('demoSlInput');
      const dTp = document.getElementById('demoTpInput');

      if (mLot && dLot) dLot.value = mLot.value;
      if (mSl && dSl) dSl.value = mSl.value;
      if (mTp && dTp) dTp.value = mTp.value;

      if (typeof executeDemoOrder === 'function') {
        executeDemoOrder(type);
      }

      // Update mobile badge and views
      updateMobileExecutionValues();
      renderMobileWalletUI();

      // Return to full chart with smooth feedback
      setTimeout(() => {
        switchMobileTab('chart');
      }, 450);
    }

    function updateMobileExecutionValues() {
      const price = typeof currentLiveSpot !== 'undefined' ? currentLiveSpot : 4007.05;
      const priceStr = '$' + price.toFixed(2);

      const liveSpot = document.getElementById('mLiveSpotPrice');
      const buyPrice = document.getElementById('mBuyTickerPrice');
      const sellPrice = document.getElementById('mSellTickerPrice');
      const topSpot = document.getElementById('mobileTopSpotPrice');

      if (liveSpot) liveSpot.innerText = priceStr;
      if (buyPrice) buyPrice.innerText = priceStr;
      if (sellPrice) sellPrice.innerText = priceStr;
      if (topSpot) topSpot.innerText = priceStr;

      if (typeof demoState !== 'undefined') {
        const totalPnl = typeof getTotalFloatingPnL === 'function' ? getTotalFloatingPnL(price) : 0;
        const equity = demoState.balance + totalPnl;
        const usedMargin = typeof getUsedMargin === 'function' ? getUsedMargin() : 0;
        const freeMargin = Math.max(0, equity - usedMargin);

        const eqEl = document.getElementById('mAccountEquity');
        const fmEl = document.getElementById('mAccountFreeMargin');
        const pnlEl = document.getElementById('mAccountFloatingPnl');

        if (eqEl) eqEl.innerText = '$' + equity.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        if (fmEl) fmEl.innerText = '$' + freeMargin.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        if (pnlEl) {
          const sign = totalPnl >= 0 ? '+' : '';
          pnlEl.innerText = sign + '$' + totalPnl.toFixed(2);
          pnlEl.style.color = totalPnl > 0 ? 'var(--green)' : (totalPnl < 0 ? 'var(--red)' : '#8b949e');
        }

        // Active positions badge
        const badge = document.getElementById('mNavPosBadge');
        if (badge) {
          if (demoState.positions && demoState.positions.length > 0) {
            badge.innerText = demoState.positions.length;
            badge.style.display = 'inline-block';
          } else {
            badge.style.display = 'none';
          }
        }
      }
    }

    function renderMobileSignalsContent() {
      const container = document.getElementById('mSignalsContainer');
      const sourceCard = document.getElementById('executionSignalsCard');
      const radarCard = document.getElementById('twelveSugraRadarCard');

      if (!container) return;
      let html = '';

      if (sourceCard) {
        html += `<div style="background: #0d1117; border: 1px solid #30363d; border-radius: 12px; padding: 14px; margin-bottom: 12px;">
          ${sourceCard.innerHTML}
        </div>`;
      }

      if (radarCard) {
        html += `<div style="background: #0d1117; border: 1px solid rgba(88, 166, 255, 0.35); border-radius: 12px; padding: 14px;">
          ${radarCard.innerHTML}
        </div>`;
      }

      container.innerHTML = html;
    }

    function renderMobileWalletUI() {
      if (typeof demoState === 'undefined') return;
      const price = typeof currentLiveSpot !== 'undefined' ? currentLiveSpot : 4007.05;
      const totalPnl = typeof getTotalFloatingPnL === 'function' ? getTotalFloatingPnL(price) : 0;
      const equity = demoState.balance + totalPnl;
      const usedMargin = typeof getUsedMargin === 'function' ? getUsedMargin() : 0;
      const freeMargin = Math.max(0, equity - usedMargin);

      const balEl = document.getElementById('mWalletBalance');
      const eqEl = document.getElementById('mWalletEquity');
      const pnlEl = document.getElementById('mWalletPnl');
      const fmEl = document.getElementById('mWalletFreeMargin');
      const posCountEl = document.getElementById('mWalletPosCount');
      const closeAllBtn = document.getElementById('mBtnCloseAll');
      const listContainer = document.getElementById('mPositionsList');

      if (balEl) balEl.innerText = '$' + demoState.balance.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
      if (eqEl) {
        eqEl.innerText = '$' + equity.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        eqEl.style.color = equity >= demoState.balance ? 'var(--green)' : 'var(--red)';
      }
      if (pnlEl) {
        const sign = totalPnl >= 0 ? '+' : '';
        pnlEl.innerText = sign + '$' + totalPnl.toFixed(2);
        pnlEl.style.color = totalPnl > 0 ? 'var(--green)' : (totalPnl < 0 ? 'var(--red)' : '#8b949e');
      }
      if (fmEl) fmEl.innerText = '$' + freeMargin.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

      if (posCountEl) posCountEl.innerText = demoState.positions.length;
      if (closeAllBtn) closeAllBtn.style.display = demoState.positions.length > 0 ? 'inline-block' : 'none';

      // Render positions list in mobile sheet
      if (listContainer) {
        if (!demoState.positions || demoState.positions.length === 0) {
          listContainer.innerHTML = '<div class="demo-empty-placeholder">No active demo positions. Tap \\'Trade\\' tab to open an order.</div>';
        } else {
          listContainer.innerHTML = demoState.positions.map(p => {
            const pnl = typeof calculatePositionPnL === 'function' ? calculatePositionPnL(p, price) : 0;
            const sign = pnl >= 0 ? '+' : '';
            const color = pnl >= 0 ? 'var(--green)' : 'var(--red)';
            const targetBadges = (p.tp || p.sl) ? `<div style="font-size: 9px; color: #8b949e;">${p.sl ? 'SL: $'+p.sl.toFixed(1) : ''} ${p.tp ? 'TP: $'+p.tp.toFixed(1) : ''}</div>` : '';
            const entryPrice = parseFloat(p.entryPrice != null ? p.entryPrice : (p.openPrice != null ? p.openPrice : 0));
            const lots = parseFloat(p.lots || 0.01);
            return `
              <div class="demo-pos-item" id="m_pos_row_${p.id}">
                <div>
                  <div style="display: flex; align-items: center; gap: 6px;">
                    <span class="demo-pos-badge ${p.type.toLowerCase()}">${p.type}</span>
                    <span style="font-weight: 700; color: #f0f6fc;">${lots.toFixed(2)}L</span>
                    <span style="color: #8b949e;">@ $${entryPrice.toFixed(2)}</span>
                  </div>
                  ${targetBadges}
                </div>
                <div style="display: flex; align-items: center; gap: 8px;">
                  <span style="font-weight: 700; color: ${color};">${sign}$${pnl.toFixed(2)}</span>
                  <button type="button" class="btn-pos-close" onclick="closeDemoPosition('${p.id}'); setTimeout(renderMobileWalletUI, 200);">Close</button>
                </div>
              </div>
            `;
          }).join('');
        }
      }

      // Update position badge on bottom nav
      const badge = document.getElementById('mNavPosBadge');
      if (badge) {
        if (demoState.positions && demoState.positions.length > 0) {
          badge.innerText = demoState.positions.length;
          badge.style.display = 'inline-block';
        } else {
          badge.style.display = 'none';
        }
      }
    }
"""

def apply_refactor(filepath):
    print(f"\n==========================================")
    print(f"Refactoring {filepath} for 100% Mobile Responsiveness...")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update viewport meta tag
    if OLD_VIEWPORT in content:
        content = content.replace(OLD_VIEWPORT, NEW_VIEWPORT)
        print(" [x] Updated viewport meta tag for mobile web app standards.")
    else:
        print(" [!] OLD_VIEWPORT not found or already updated.")

    # 2. Add Mobile Timeframe Pill Row in Subheader
    if TARGET_SUBHEADER in content:
        content = content.replace(TARGET_SUBHEADER, REPLACEMENT_SUBHEADER)
        print(" [x] Injected mobile horizontally scrollable timeframe pill bar.")
    else:
        print(" [!] TARGET_SUBHEADER not found.")

    # 3. Add Mobile Bottom Navigation & Slide-Up Bottom Sheets
    if TARGET_BOTTOM_TERMINAL in content:
        content = content.replace(TARGET_BOTTOM_TERMINAL, REPLACEMENT_BOTTOM_TERMINAL)
        print(" [x] Injected TradingView/Exness bottom nav dock and modal bottom sheets.")
    else:
        print(" [!] TARGET_BOTTOM_TERMINAL not found.")

    # 4. Inject Mobile CSS into <style>
    style_end = '</style>'
    if style_end in content:
        content = content.replace(style_end, MOBILE_RESPONSIVE_CSS + '\n  ' + style_end, 1)
        print(" [x] Injected complete mobile responsive CSS into stylesheet.")
    else:
        print(" [!] </style> tag not found.")

    # 5. Update Lightweight Charts Touch Options
    if TARGET_CHART_OPTIONS in content:
        content = content.replace(TARGET_CHART_OPTIONS, REPLACEMENT_CHART_OPTIONS)
        print(" [x] Updated Lightweight Charts with handleTouch, pinchToZoom, and touch crosshairs.")
    else:
        print(" [!] TARGET_CHART_OPTIONS not found.")

    # 6. Hook Mobile Timeframe Sync into selectTimeframe(tf)
    target_tf_func = "      switchTimeframe(tf);"
    replacement_tf_func = """      document.querySelectorAll('.mobile-tf-pill').forEach(pill => {
        pill.classList.toggle('active', pill.getAttribute('data-tf') === tf);
      });
      switchTimeframe(tf);"""
    if target_tf_func in content:
        content = content.replace(target_tf_func, replacement_tf_func, 1)
        print(" [x] Hooked mobile timeframe pill sync into selectTimeframe().")

    # 7. Hook Mobile Wallet Sync into renderDemoWalletUI
    target_wallet_render = "      if (closeAllBtn) closeAllBtn.style.display = demoState.positions.length > 0 ? 'inline-block' : 'none';"
    replacement_wallet_render = """      if (closeAllBtn) closeAllBtn.style.display = demoState.positions.length > 0 ? 'inline-block' : 'none';
      if (typeof updateMobileExecutionValues === 'function') updateMobileExecutionValues();"""
    if target_wallet_render in content:
        content = content.replace(target_wallet_render, replacement_wallet_render, 1)
        print(" [x] Hooked real-time mobile execution sync into renderDemoWalletUI().")

    # 8. Inject Mobile JS Handlers before </script>
    last_script_end = content.rfind('</script>')
    if last_script_end != -1:
        content = content[:last_script_end] + MOBILE_JS_HANDLERS + '\n  ' + content[last_script_end:]
        print(" [x] Injected mobile JavaScript event handlers.")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f" [SUCCESS] Saved {filepath} ({len(content):,} bytes)")

if __name__ == '__main__':
    for fn in ['gold_dashboard.html', 'index.html', 'deep_analysis_gold.html']:
        apply_refactor(fn)
