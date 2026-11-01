"""
Apply complete TradingView & Exness mobile responsiveness to gold_dashboard.html, index.html, deep_analysis_gold.html.
"""

import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

TARGET_BOTTOM_TERMINAL = """      </aside>
    </div>
  </div>"""

REPLACEMENT_BOTTOM_TERMINAL = """      </aside>
    </div>

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
            <span id="mobileSheetTitle" class="mobile-sheet-title-text">Quick Execution Pad</span>
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
            <!-- Dynamically populated from executionSignalsCard & twelveSugraRadarCard -->
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
  </div>"""

def inject_bottom_markup(filepath):
    print(f"Injecting bottom nav and sheets into {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if TARGET_BOTTOM_TERMINAL in content:
        content = content.replace(TARGET_BOTTOM_TERMINAL, REPLACEMENT_BOTTOM_TERMINAL, 1)
        print(" [x] Injected mobile bottom navigation and modal bottom sheets.")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f" [SUCCESS] Saved {filepath} ({len(content):,} bytes)")
    else:
        print(" [!] TARGET_BOTTOM_TERMINAL not found in file!")

if __name__ == '__main__':
    for fn in ['gold_dashboard.html', 'index.html', 'deep_analysis_gold.html']:
        inject_bottom_markup(fn)
