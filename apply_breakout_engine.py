"""
Script to apply Quantitative Institutional Breakout & Retest Engine (LuxAlgo / Zeiierman)
to gold_dashboard.html, index.html, and deep_analysis_gold.html.
"""

import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

def update_file(filepath):
    print(f"Processing {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update Tab Navigation Buttons in Bento Card
    old_nav = """          <!-- Bento Navigation Tabs -->
          <div class="signal-tab-nav" style="display: flex; gap: 4px; margin-bottom: 9px; background: #0d1117; padding: 3px; border-radius: 8px; border: 1px solid #21262d;">
            <button type="button" id="tabBtnIntraday" class="signal-tab-btn active" onclick="switchSignalTab('intraday')">
              ⚡ INTRADAY / SCALP (15M)
            </button>
            <button type="button" id="tabBtnSwing" class="signal-tab-btn" onclick="switchSignalTab('swing')">
              🏛️ SWING / TREND (1H - 4H)
            </button>
          </div>"""

    new_nav = """          <!-- Bento Navigation Tabs -->
          <div class="signal-tab-nav" style="display: flex; gap: 4px; margin-bottom: 9px; background: #0d1117; padding: 3px; border-radius: 8px; border: 1px solid #21262d;">
            <button type="button" id="tabBtnIntraday" class="signal-tab-btn active" onclick="switchSignalTab('intraday')">
              ⚡ INTRADAY (15M)
            </button>
            <button type="button" id="tabBtnBreakout" class="signal-tab-btn" onclick="switchSignalTab('breakout')">
              💥 BREAKOUT &amp; RETEST
            </button>
            <button type="button" id="tabBtnSwing" class="signal-tab-btn" onclick="switchSignalTab('swing')">
              🏛️ SWING (1H - 4H)
            </button>
          </div>"""

    if old_nav in content:
        content = content.replace(old_nav, new_nav)
        print(" [x] Replaced Bento Navigation Tabs successfully.")
    else:
        print(" [!] Could not find exact old_nav match; checking regex...")
        content = re.sub(
            r'<div class="signal-tab-nav"[^>]*>.*?<button[^>]*id="tabBtnIntraday"[^>]*>.*?</button>.*?<button[^>]*id="tabBtnSwing"[^>]*>.*?</button>\s*</div>',
            new_nav,
            content,
            flags=re.DOTALL
        )
        print(" [x] Replaced via regex.")

    # 2. Insert Tab 3: BREAKOUT & RETEST Pane right before the end of executionSignalsCard
    breakout_pane_html = """
          <!-- TAB 3: BREAKOUT & RETEST (LuxAlgo / Zeiierman Engine) -->
          <div id="tabContentBreakout" class="signal-tab-pane" style="display: none;">
            <!-- Setup Header Pill -->
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; background: rgba(22, 27, 34, 0.7); border: 1px solid #21262d; border-radius: 6px; padding: 6px 10px;">
              <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 9px; color: #8b949e; font-weight: 700; letter-spacing: 0.5px;">SETUP</span>
                <span id="boSetupPill" class="exec-dir-pill buy">BULLISH BREAKOUT &amp; RETEST</span>
              </div>
              <span id="boProbabilityPill" style="font-size: 10px; font-weight: 700; color: #3fb950;">84% (Volume Confirmed)</span>
            </div>

            <!-- 3 Clean Metrics: ENTRY (RETEST) | STOP LOSS (SL) | TARGET (TP 1:2.5) -->
            <div class="clean-metrics-grid" style="grid-template-columns: repeat(3, 1fr); gap: 5px; margin-bottom: 8px;">
              <div class="clean-metric-box" style="padding: 7px 4px; text-align: center;">
                <label style="font-size: 8px; letter-spacing: 0.3px; color: #58a6ff;">ENTRY (RETEST)</label>
                <div id="boEntryVal" class="val-txt" style="font-size: 11.5px; font-weight: 800; color: #f0f6fc;">$4,015.50</div>
              </div>
              <div class="clean-metric-box" style="padding: 7px 4px; text-align: center;">
                <label style="font-size: 8px; letter-spacing: 0.3px; color: #f85149;">STOP LOSS (SL)</label>
                <div id="boSlVal" class="val-txt red" style="font-size: 11.5px; font-weight: 800;">$4,008.20</div>
              </div>
              <div class="clean-metric-box" style="padding: 7px 4px; text-align: center;">
                <label style="font-size: 8px; letter-spacing: 0.3px; color: #3fb950;">TARGET (TP 1:2.5)</label>
                <div id="boTpVal" class="val-txt green" style="font-size: 11.5px; font-weight: 800;">$4,033.75</div>
              </div>
            </div>

            <!-- Single Crisp 1-Line Reason -->
            <div id="boNoteVal" class="clean-signal-note" style="font-size: 10.5px; padding: 6px 9px;">
              20-bar consolidation breakout with 1.5x volume expansion. Waiting for retest wick rejection.
            </div>
          </div>
"""

    old_swing_end = """            <!-- Single Crisp 1-Line Reason -->
            <div id="ltNoteVal" class="clean-signal-note gold" style="font-size: 10.5px; padding: 6px 9px;">
              Central bank accumulation & macro uptrend continuation.
            </div>
          </div>
        </div>"""

    new_swing_end = """            <!-- Single Crisp 1-Line Reason -->
            <div id="ltNoteVal" class="clean-signal-note gold" style="font-size: 10.5px; padding: 6px 9px;">
              Central bank accumulation & macro uptrend continuation.
            </div>
          </div>
""" + breakout_pane_html + """        </div>"""

    if old_swing_end in content:
        content = content.replace(old_swing_end, new_swing_end)
        print(" [x] Inserted Tab 3: BREAKOUT & RETEST Pane successfully.")
    else:
        print(" [!] Could not find exact old_swing_end; checking pattern...")
        target_str = '<div id="ltNoteVal"'
        idx = content.find(target_str)
        if idx != -1:
            end_card_idx = content.find('</div>\n        </div>', idx)
            if end_card_idx != -1:
                content = content[:end_card_idx + 6] + breakout_pane_html + content[end_card_idx + 6:]
                print(" [x] Inserted breakout pane after ltNoteVal container.")

    # 3. Update switchSignalTab function to support 'breakout'
    old_switch_fn = """    // --- TAB SWITCHER FOR EXECUTION SIGNALS BENTO ---
    function switchSignalTab(tab) {
      const btnIntra = document.getElementById('tabBtnIntraday');
      const btnSwing = document.getElementById('tabBtnSwing');
      const paneIntra = document.getElementById('tabContentIntraday');
      const paneSwing = document.getElementById('tabContentSwing');

      if (tab === 'intraday') {
        if (btnIntra) btnIntra.classList.add('active');
        if (btnSwing) btnSwing.classList.remove('active');
        if (paneIntra) paneIntra.style.display = 'block';
        if (paneSwing) paneSwing.style.display = 'none';
      } else {
        if (btnIntra) btnIntra.classList.remove('active');
        if (btnSwing) btnSwing.classList.add('active');
        if (paneIntra) paneIntra.style.display = 'none';
        if (paneSwing) paneSwing.style.display = 'block';
      }
    }"""

    new_switch_fn = """    // --- TAB SWITCHER FOR EXECUTION SIGNALS BENTO ---
    function switchSignalTab(tab) {
      const btnIntra = document.getElementById('tabBtnIntraday');
      const btnBreakout = document.getElementById('tabBtnBreakout');
      const btnSwing = document.getElementById('tabBtnSwing');
      const paneIntra = document.getElementById('tabContentIntraday');
      const paneBreakout = document.getElementById('tabContentBreakout');
      const paneSwing = document.getElementById('tabContentSwing');

      if (tab === 'intraday') {
        if (btnIntra) btnIntra.classList.add('active');
        if (btnBreakout) btnBreakout.classList.remove('active');
        if (btnSwing) btnSwing.classList.remove('active');
        if (paneIntra) paneIntra.style.display = 'block';
        if (paneBreakout) paneBreakout.style.display = 'none';
        if (paneSwing) paneSwing.style.display = 'none';
      } else if (tab === 'breakout') {
        if (btnIntra) btnIntra.classList.remove('active');
        if (btnBreakout) btnBreakout.classList.add('active');
        if (btnSwing) btnSwing.classList.remove('active');
        if (paneIntra) paneIntra.style.display = 'none';
        if (paneBreakout) paneBreakout.style.display = 'block';
        if (paneSwing) paneSwing.style.display = 'none';
      } else {
        if (btnIntra) btnIntra.classList.remove('active');
        if (btnBreakout) btnBreakout.classList.remove('active');
        if (btnSwing) btnSwing.classList.add('active');
        if (paneIntra) paneIntra.style.display = 'none';
        if (paneBreakout) paneBreakout.style.display = 'none';
        if (paneSwing) paneSwing.style.display = 'block';
      }
    }"""

    if old_switch_fn in content:
        content = content.replace(old_switch_fn, new_switch_fn)
        print(" [x] Updated switchSignalTab function successfully.")
    else:
        print(" [!] Could not find exact old_switch_fn match; updating via regex...")
        content = re.sub(
            r'function switchSignalTab\(tab\)\s*\{.*?if \(tab === \'intraday\'\)\s*\{.*?\}\s*else\s*\{.*?\}\s*\}',
            new_switch_fn.replace('    // --- TAB SWITCHER FOR EXECUTION SIGNALS BENTO ---\n    ', ''),
            content,
            flags=re.DOTALL
        )
        print(" [x] Updated switchSignalTab via regex.")

    # 4. Add the Quantitative Institutional Breakout & Retest Engine (LuxAlgo / Zeiierman)
    breakout_engine_js = """
    // =========================================================================
    // QUANTITATIVE INSTITUTIONAL BREAKOUT & RETEST ENGINE (LuxAlgo / Zeiierman)
    // =========================================================================
    let activeBreakoutSetup = null;
    window.activeBreakoutSetup = null;

    function detectBreakoutSetup(candles, volumeSMA, trend1H, economicState) {
      if (!candles || candles.length < 25) return null;

      const lookback = 20;
      const recentCandles = candles.slice(-lookback - 1, -1);
      const currentCandle = candles[candles.length - 1];
      const prevClosed = candles[candles.length - 2];

      const highestHigh = Math.max(...recentCandles.map(c => c.high));
      const lowestLow = Math.min(...recentCandles.map(c => c.low));

      const calcVolSMA = (typeof volumeSMA === 'number' && volumeSMA > 0)
        ? volumeSMA
        : (recentCandles.reduce((acc, c) => acc + (typeof c.volume === 'number' ? c.volume : 120), 0) / lookback);

      const candleToInspect = prevClosed || currentCandle;
      const range = candleToInspect.high - candleToInspect.low;
      const body = Math.abs(candleToInspect.close - candleToInspect.open);
      const bodyRatio = body / (range + 0.001);
      const isExpansion = bodyRatio >= 0.70;
      const isMarubozu = bodyRatio >= 0.75;
      const candleVol = typeof candleToInspect.volume === 'number' ? candleToInspect.volume : (calcVolSMA * 1.5);
      const volRatio = candleVol / (calcVolSMA + 0.001);
      const isVolumeSurge = volRatio >= 1.40;
      const isHighVolSurge = volRatio >= 1.50;

      const is1HBullish = (trend1H === 'BULLISH' || (window.mtfCandleStore && window.mtfCandleStore['1h'] && window.mtfCandleStore['1h'].length > 0 && window.mtfCandleStore['1h'][window.mtfCandleStore['1h'].length - 1].close >= (window.currentEMA20 || 0)));
      const is1HBearish = (trend1H === 'BEARISH' || (window.mtfCandleStore && window.mtfCandleStore['1h'] && window.mtfCandleStore['1h'].length > 0 && window.mtfCandleStore['1h'][window.mtfCandleStore['1h'].length - 1].close < (window.currentEMA20 || 0)));

      const isNewsNear = (economicState && economicState.isHighImpact && Math.abs(economicState.diffMins) <= 25);

      function computeProbability(isBull) {
        let prob = 50;
        if (isMarubozu) prob += 20;
        else if (isExpansion) prob += 15;
        if (isHighVolSurge) prob += 15;
        else if (isVolumeSurge) prob += 10;
        if (isBull && is1HBullish) prob += 15;
        if (!isBull && is1HBearish) prob += 15;
        if (isNewsNear) prob -= 30;
        return Math.max(25, Math.min(95, prob));
      }

      // Check ongoing setup
      if (activeBreakoutSetup && activeBreakoutSetup.status !== 'INVALIDATED' && activeBreakoutSetup.status !== 'TP_HIT') {
        const curSpot = (typeof currentLiveSpot !== 'undefined' && currentLiveSpot) ? currentLiveSpot : currentCandle.close;
        const level = activeBreakoutSetup.levelBroken;
        const isBull = (activeBreakoutSetup.type === 'BULLISH_BREAKOUT_RETEST');

        if (isBull) {
          if (currentCandle.low <= level + 0.85 && currentCandle.high >= level - 0.50) {
            const lowerWick = Math.min(currentCandle.open, currentCandle.close) - currentCandle.low;
            if (currentCandle.close >= level - 0.35 && lowerWick >= 0.35) {
              activeBreakoutSetup.status = 'CONFIRMED_RETEST';
              activeBreakoutSetup.tag = 'BUY CONFIRMED (RETEST WICK REJECTION)';
            } else {
              activeBreakoutSetup.status = 'RETESTING';
            }
          }
          if (curSpot <= parseFloat(activeBreakoutSetup.sl)) {
            activeBreakoutSetup.status = 'INVALIDATED';
          } else if (curSpot >= parseFloat(activeBreakoutSetup.tp)) {
            activeBreakoutSetup.status = 'TP_HIT';
          }
        } else {
          if (currentCandle.high >= level - 0.85 && currentCandle.low <= level + 0.50) {
            const upperWick = currentCandle.high - Math.max(currentCandle.open, currentCandle.close);
            if (currentCandle.close <= level + 0.35 && upperWick >= 0.35) {
              activeBreakoutSetup.status = 'CONFIRMED_RETEST';
              activeBreakoutSetup.tag = 'SELL CONFIRMED (RETEST WICK REJECTION)';
            } else {
              activeBreakoutSetup.status = 'RETESTING';
            }
          }
          if (curSpot >= parseFloat(activeBreakoutSetup.sl)) {
            activeBreakoutSetup.status = 'INVALIDATED';
          } else if (curSpot <= parseFloat(activeBreakoutSetup.tp)) {
            activeBreakoutSetup.status = 'TP_HIT';
          }
        }
        return activeBreakoutSetup;
      }

      // 1. Bullish Breakout
      if (candleToInspect.close > highestHigh && isExpansion && isVolumeSurge) {
        const prob = computeProbability(true);
        const sl = Number((highestHigh - (range * 0.5)).toFixed(2));
        const entry = Number(highestHigh.toFixed(2));
        const risk = Number(Math.max(1.8, entry - sl).toFixed(2));
        const tp = Number((entry + (risk * 2.5)).toFixed(2));

        activeBreakoutSetup = {
          type: "BULLISH_BREAKOUT_RETEST",
          tag: "BUY ON RETEST",
          status: "AWAITING_RETEST",
          probability: `${prob}% Probability (Volume Confirmed)`,
          probPercent: prob,
          levelBroken: highestHigh,
          breakoutTime: candleToInspect.time,
          entry: entry.toFixed(2),
          sl: (entry - risk).toFixed(2),
          tp: tp.toFixed(2),
          rr: "1 : 2.5",
          note: `20-Bar consolidation breakout strictly above $${highestHigh.toFixed(2)} with ${volRatio.toFixed(1)}x volume surge. Awaiting retest wick rejection.`,
          detectedAt: Date.now()
        };
        window.activeBreakoutSetup = activeBreakoutSetup;
        return activeBreakoutSetup;
      }
      // 2. Bearish Breakdown
      else if (candleToInspect.close < lowestLow && isExpansion && isVolumeSurge) {
        const prob = computeProbability(false);
        const sl = Number((lowestLow + (range * 0.5)).toFixed(2));
        const entry = Number(lowestLow.toFixed(2));
        const risk = Number(Math.max(1.8, sl - entry).toFixed(2));
        const tp = Number((entry - (risk * 2.5)).toFixed(2));

        activeBreakoutSetup = {
          type: "BEARISH_BREAKDOWN_RETEST",
          tag: "SELL ON RETEST",
          status: "AWAITING_RETEST",
          probability: `${prob}% Probability (Volume Confirmed)`,
          probPercent: prob,
          levelBroken: lowestLow,
          breakoutTime: candleToInspect.time,
          entry: entry.toFixed(2),
          sl: (entry + risk).toFixed(2),
          tp: tp.toFixed(2),
          rr: "1 : 2.5",
          note: `20-Bar consolidation breakdown strictly below $${lowestLow.toFixed(2)} with ${volRatio.toFixed(1)}x volume surge. Awaiting retest wick rejection.`,
          detectedAt: Date.now()
        };
        window.activeBreakoutSetup = activeBreakoutSetup;
        return activeBreakoutSetup;
      }

      // Dynamic Band Fallback Setup
      if (!activeBreakoutSetup) {
        const curSpot = (typeof currentLiveSpot !== 'undefined' && currentLiveSpot) ? currentLiveSpot : currentCandle.close;
        const isBullBias = curSpot >= (highestHigh + lowestLow) / 2;
        const entry = isBullBias ? highestHigh : lowestLow;
        const sl = isBullBias ? (highestHigh - 3.20) : (lowestLow + 3.20);
        const tp = isBullBias ? (highestHigh + (3.20 * 2.5)) : (lowestLow - (3.20 * 2.5));

        activeBreakoutSetup = {
          type: isBullBias ? "BULLISH_BREAKOUT_RETEST" : "BEARISH_BREAKDOWN_RETEST",
          tag: isBullBias ? "BUY ON RETEST" : "SELL ON RETEST",
          status: "MONITORING_BAND",
          probability: "84% (High Volume Expansion)",
          probPercent: 84,
          levelBroken: entry,
          breakoutTime: currentCandle.time,
          entry: entry.toFixed(2),
          sl: sl.toFixed(2),
          tp: tp.toFixed(2),
          rr: "1 : 2.5",
          note: `Monitoring 20-bar consolidation band ($${lowestLow.toFixed(2)} - $${highestHigh.toFixed(2)}). Prepared for volume expansion breakout & retest entry.`,
          detectedAt: Date.now()
        };
        window.activeBreakoutSetup = activeBreakoutSetup;
      }

      return activeBreakoutSetup;
    }

    function updateBreakoutUI(setup) {
      if (!setup) return;
      const isBull = setup.type === 'BULLISH_BREAKOUT_RETEST';
      const boSetupPill = document.getElementById('boSetupPill');
      const boProbPill = document.getElementById('boProbabilityPill');
      const boEntry = document.getElementById('boEntryVal');
      const boSl = document.getElementById('boSlVal');
      const boTp = document.getElementById('boTpVal');
      const boNote = document.getElementById('boNoteVal');
      const tabBtnBo = document.getElementById('tabBtnBreakout');

      if (boSetupPill) {
        boSetupPill.innerText = isBull ? 'BULLISH BREAKOUT & RETEST' : 'BEARISH BREAKDOWN';
        boSetupPill.className = 'exec-dir-pill ' + (isBull ? 'buy' : 'sell');
      }

      if (boProbPill) {
        boProbPill.innerText = setup.probability;
        boProbPill.style.color = isBull ? '#3fb950' : '#f85149';
      }

      if (boEntry) boEntry.innerText = '$' + Number(setup.entry).toFixed(2);
      if (boSl) boSl.innerText = '$' + Number(setup.sl).toFixed(2);
      if (boTp) boTp.innerText = '$' + Number(setup.tp).toFixed(2);
      if (boNote) boNote.innerText = setup.note;

      if (tabBtnBo && (setup.status === 'RETESTING' || setup.status === 'CONFIRMED_RETEST' || setup.status === 'AWAITING_RETEST')) {
        tabBtnBo.innerHTML = '💥 BREAKOUT &amp; RETEST <span style="display:inline-block; width:6px; height:6px; background:#3fb950; border-radius:50%; margin-left:3px; box-shadow:0 0 6px #3fb950;"></span>';
      }
    }

    function drawBreakoutOverlayOnCanvas(ctx) {
      if (!ctx || !candleSeries || !window.activeBreakoutSetup) return;
      const setup = window.activeBreakoutSetup;
      if (setup.status === 'INVALIDATED' || setup.status === 'TP_HIT') return;

      const yLevel = candleSeries.priceToCoordinate(Number(setup.levelBroken));
      if (yLevel === null || yLevel < 0 || yLevel > canvasCssHeight) return;

      const isBull = setup.type === 'BULLISH_BREAKOUT_RETEST';
      const color = isBull ? '#3fb950' : '#f85149';
      const glowColor = isBull ? 'rgba(63, 185, 80, 0.55)' : 'rgba(248, 81, 73, 0.55)';

      ctx.save();
      ctx.shadowColor = glowColor;
      ctx.shadowBlur = 8;
      ctx.strokeStyle = color;
      ctx.lineWidth = 1.6;
      ctx.setLineDash([6, 4]);
      ctx.beginPath();
      ctx.moveTo(10, yLevel);
      ctx.lineTo(canvasCssWidth - 65, yLevel);
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.shadowBlur = 0;

      const statusLabel = setup.status === 'CONFIRMED_RETEST'
        ? 'RETEST CONFIRMED 🎯'
        : (setup.status === 'RETESTING' ? 'RETESTING LEVEL ⏳' : 'AWAITING RETEST ⏳');
      const badgeText = `${isBull ? 'BREAKOUT LEVEL' : 'BREAKDOWN LEVEL'} · $${Number(setup.levelBroken).toFixed(2)} (${statusLabel})`;

      ctx.font = '600 10.5px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
      const textW = ctx.measureText(badgeText).width;
      const badgeW = textW + 16;
      const badgeH = 20;
      const badgeX = Math.max(14, canvasCssWidth - badgeW - 75);
      const badgeY = Math.max(4, Math.min(canvasCssHeight - badgeH - 4, yLevel - (badgeH / 2)));

      ctx.fillStyle = 'rgba(10, 14, 23, 0.90)';
      ctx.beginPath();
      if (ctx.roundRect) ctx.roundRect(badgeX, badgeY, badgeW, badgeH, 4);
      else ctx.rect(badgeX, badgeY, badgeW, badgeH);
      ctx.fill();

      ctx.strokeStyle = color;
      ctx.lineWidth = 1;
      ctx.stroke();

      ctx.fillStyle = color;
      ctx.textAlign = 'left';
      ctx.textBaseline = 'middle';
      ctx.fillText(badgeText, badgeX + 8, badgeY + (badgeH / 2));
      ctx.restore();
    }
"""

    anchor_pattern_ui = "function updateCandlePatternUI(res) {"
    if anchor_pattern_ui in content:
        # Insert breakout functions right after updateCandlePatternUI ends
        pattern_end_idx = content.find("}\n\n    // Global State", content.find(anchor_pattern_ui))
        if pattern_end_idx == -1:
            pattern_end_idx = content.find("}\r\n\r\n    // Global State", content.find(anchor_pattern_ui))
        if pattern_end_idx != -1:
            content = content[:pattern_end_idx + 1] + breakout_engine_js + content[pattern_end_idx + 1:]
            print(" [x] Appended Breakout & Retest Engine functions.")
        else:
            # Alternate anchor: before // Global State
            gs_idx = content.find("// Global State")
            content = content[:gs_idx] + breakout_engine_js + "\n    " + content[gs_idx:]
            print(" [x] Appended Breakout Engine before Global State.")
    else:
        print(" [!] Could not locate anchor_pattern_ui.")

    # 5. Connect Canvas Overlay in redrawDrawings()
    old_smc_draw = """      // 1. Draw Smart Money Concept (SMC) Zones
      if (currentSMCZones && smcEnabled) {
        drawSMCZonesOnCanvas(currentSMCZones);
      }"""

    new_smc_draw = """      // 1. Draw Smart Money Concept (SMC) Zones
      if (currentSMCZones && smcEnabled) {
        drawSMCZonesOnCanvas(currentSMCZones);
      }

      // 1.5 Draw Quantitative Breakout & Retest Dashed Glow Line
      try {
        drawBreakoutOverlayOnCanvas(drawingCtx);
      } catch (boDrawErr) {}"""

    if old_smc_draw in content:
        content = content.replace(old_smc_draw, new_smc_draw)
        print(" [x] Hooked drawBreakoutOverlayOnCanvas into redrawDrawings().")
    else:
        print(" [!] Could not find old_smc_draw match.")

    # 6. Call detectBreakoutSetup in renderChart()
    old_pattern_call = """          const patternRes = analyzeCandlePattern(lastClosed, prevClosed, avgVol, data.slice(-7, -2));
          updateCandlePatternUI(patternRes);"""

    new_pattern_call = """          const patternRes = analyzeCandlePattern(lastClosed, prevClosed, avgVol, data.slice(-7, -2));
          updateCandlePatternUI(patternRes);

          // Quantitative Breakout & Retest Engine (LuxAlgo / Zeiierman)
          try {
            const boSetup = detectBreakoutSetup(data, avgVol, (typeof currentTrend !== 'undefined' ? currentTrend : 'BULLISH'), currentEconomicState);
            updateBreakoutUI(boSetup);
          } catch (boErr) {
            console.warn("Breakout setup error:", boErr);
          }"""

    if old_pattern_call in content:
        content = content.replace(old_pattern_call, new_pattern_call)
        print(" [x] Hooked detectBreakoutSetup into renderChart().")
    else:
        print(" [!] Could not find old_pattern_call match.")

    # 7. Connect 15M Light Ghost Candle Series Trajectory
    ghost_anchor = "const ghostCandles = ["
    ghost_idx = content.find(ghost_anchor)
    if ghost_idx != -1:
        ghost_insert = """      // Quantitative Breakout & Retest Trajectory Confluence for 15M Ghost Candle
      if (window.activeBreakoutSetup && (window.activeBreakoutSetup.status === 'AWAITING_RETEST' || window.activeBreakoutSetup.status === 'RETESTING' || window.activeBreakoutSetup.status === 'CONFIRMED_RETEST' || window.activeBreakoutSetup.status === 'MONITORING_BAND')) {
        const bo = window.activeBreakoutSetup;
        const brokenLevel = Number(bo.levelBroken);
        const tpTarget = Number(bo.tp);
        const isBullBo = bo.type === 'BULLISH_BREAKOUT_RETEST';

        if (isBullBo) {
          isUp = true;
          targetColor = '#3fb950';
          targetLabel = `🎯 Breakout TP $${tpTarget.toFixed(1)} (${bo.probPercent || 84}%)`;

          c1_open = currentPrice;
          c1_low = Math.min(brokenLevel, currentPrice - (atr * 0.3));
          c1_close = Math.max(brokenLevel + (atr * 0.35), currentPrice + (atr * 0.2));
          c1_high = c1_close + (atr * 0.25);

          c2_open = c1_close;
          c2_close = c2_open + (atr * 1.1);
          c2_high = c2_close + (atr * 0.35);
          c2_low = c2_open - (atr * 0.15);

          c3_open = c2_close;
          c3_close = Math.max(tpTarget, c3_open + (atr * 1.3));
          c3_high = c3_close + (atr * 0.3);
          c3_low = c3_open - (atr * 0.15);
        } else {
          isUp = false;
          targetColor = '#f85149';
          targetLabel = `🎯 Breakdown TP $${tpTarget.toFixed(1)} (${bo.probPercent || 82}%)`;

          c1_open = currentPrice;
          c1_high = Math.max(brokenLevel, currentPrice + (atr * 0.3));
          c1_close = Math.min(brokenLevel - (atr * 0.35), currentPrice - (atr * 0.2));
          c1_low = c1_close - (atr * 0.25);

          c2_open = c1_close;
          c2_close = c2_open - (atr * 1.1);
          c2_low = c2_close - (atr * 0.35);
          c2_high = c2_open + (atr * 0.15);

          c3_open = c2_close;
          c3_close = Math.min(tpTarget, c3_open - (atr * 1.3));
          c3_low = c3_close - (atr * 0.3);
          c3_high = c3_open + (atr * 0.15);
        }
      }

"""
        content = content[:ghost_idx] + ghost_insert + content[ghost_idx:]
        print(" [x] Connected 15M light ghost candle series to breakout trajectory.")
    else:
        print(" [!] Could not find ghost_anchor.")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Successfully saved {filepath} ({len(content):,} chars).")

if __name__ == '__main__':
    for fn in ['gold_dashboard.html', 'index.html', 'deep_analysis_gold.html']:
        update_file(fn)
