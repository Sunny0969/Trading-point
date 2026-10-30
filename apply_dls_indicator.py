# apply_dls_indicator.py
import re

with open('gold_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add toggle in tvIndicatorsMenu
target_menu = """            <!-- Indicator: Liquidity & Candle Psychology Engine (Sweep + Multi-Bar Confirmation) -->
            <div class="tv-ind-row" onclick="clickModularToggle('liquidityPsychology', event)">
              <div class="tv-ind-info">
                <div style="display: flex; align-items: center; gap: 6px;">
                  <b style="color: #00e5ff;">⚡ Liquidity &amp; Candle Psychology (Sweep + Multi-Bar Confirmation)</b>
                  <span style="font-size: 9px; background: rgba(0,229,255,0.18); color: #00e5ff; padding: 1px 4px; border-radius: 4px; font-weight: 700;">WT: 25%</span>
                </div>
                <small>Sweep + 5-Candle Psychology Window &amp; Absorption Protocol</small>
              </div>
              <label class="toggle-switch" onclick="event.stopPropagation()">
                <input type="checkbox" id="ind-toggle-liquidityPsychology" checked onchange="toggleModularIndicator('liquidityPsychology')">
                <span class="toggle-slider"></span>
              </label>
            </div>"""

repl_menu = target_menu + """

            <!-- Indicator: Daily Liquidity Sniper (1D Sweep + 1M Trigger) -->
            <div class="tv-ind-row" onclick="clickModularToggle('dailyLiquiditySniper', event)">
              <div class="tv-ind-info">
                <div style="display: flex; align-items: center; gap: 6px;">
                  <b style="color: #ffd700;">⚡ Daily Liquidity Sniper (PDH/PDL 1M Breakout)</b>
                  <span style="font-size: 9px; background: rgba(255,215,0,0.18); color: #ffd700; padding: 1px 4px; border-radius: 4px; font-weight: 700;">WT: 25%</span>
                </div>
                <small>1D PDH/PDL Sweep + 1M Micro Candle Low/High Breakout Confirmation</small>
              </div>
              <label class="toggle-switch" onclick="event.stopPropagation()">
                <input type="checkbox" id="ind-toggle-dailyLiquiditySniper" checked onchange="toggleModularIndicator('dailyLiquiditySniper')">
                <span class="toggle-slider"></span>
              </label>
            </div>"""

assert target_menu in content, "target_menu not found in content"
content = content.replace(target_menu, repl_menu, 1)

# 2. Add toggle in modal
target_modal = """        <div class="indicator-row">
          <div>
            <div style="display: flex; align-items: center; gap: 6px;">
              <b style="color: #00e5ff;">⚡ Liquidity &amp; Candle Psychology (Sweep + Multi-Bar Confirmation)</b>
              <span style="font-size: 9px; background: rgba(0,229,255,0.18); color: #00e5ff; padding: 1px 4px; border-radius: 4px; font-weight: 700;">WT: 25%</span>
            </div>
            <p style="font-size: 11px; color: #8b949e; margin: 2px 0 0;">Sweep + 5-Candle Psychology Window &amp; Absorption Protocol</p>
          </div>
          <label class="toggle-switch">
            <input type="checkbox" id="modal-toggle-liquidityPsychology" checked onchange="toggleModularIndicator('liquidityPsychology')">
            <span class="toggle-slider"></span>
          </label>
        </div>"""

repl_modal = target_modal + """

        <div class="indicator-row">
          <div>
            <div style="display: flex; align-items: center; gap: 6px;">
              <b style="color: #ffd700;">⚡ Daily Liquidity Sniper (PDH/PDL 1M Breakout)</b>
              <span style="font-size: 9px; background: rgba(255,215,0,0.18); color: #ffd700; padding: 1px 4px; border-radius: 4px; font-weight: 700;">WT: 25%</span>
            </div>
            <p style="font-size: 11px; color: #8b949e; margin: 2px 0 0;">1D PDH/PDL Sweep + 1M Micro Candle Low/High Breakout Confirmation</p>
          </div>
          <label class="toggle-switch">
            <input type="checkbox" id="modal-toggle-dailyLiquiditySniper" checked onchange="toggleModularIndicator('dailyLiquiditySniper')">
            <span class="toggle-slider"></span>
          </label>
        </div>"""

assert target_modal in content, "target_modal not found in content"
content = content.replace(target_modal, repl_modal, 1)

# 3. Add pipeline pill in stModularPipelineGrid
target_grid = """<span id="pipeLiqPsy" class="pipe-step-pill active" title="Step 3: Liquidity &amp; Candle Psychology">⚡ Liq Psy: 5-Bar Confirmed</span>"""
repl_grid = target_grid + """\n              <span id="pipeDLS" class="pipe-step-pill active" title="Step 3.5: Daily Liquidity Sniper (PDH/PDL 1M Breakout)">⚡ DLS-1M: Active</span>"""

assert target_grid in content, "target_grid not found in content"
content = content.replace(target_grid, repl_grid, 1)

# 4. Update DEFAULT_INDICATOR_CONFIG and MODULE_WEIGHTS
target_cfg = """    const DEFAULT_INDICATOR_CONFIG = {
      smcZones: true,        // Module 1: SMC Zones (FVG & Order Blocks) - Weight: 25
      liquidityHunter: true, // Module 2: Liquidity & Order Flow Hunter (Session Sweeps, EQH/EQL) - Weight: 25
      liquidityPsychology: true, // Dedicated: Liquidity & Candle Psychology Engine (Sweep + 5-Candle Confirmation) - Weight: 25
      autoFib: true,         // Module 3: Auto Fibonacci Golden Pocket (0.50 - 0.618) - Weight: 20
      priceAction: true,     // Module 4: Price Action & Candlestick Scanner - Weight: 15
      momentumSuite: false   // Module 5: Momentum & Trend Suite (EMA 20/50, RSI, MACD) - Weight: 15
    };

    const MODULE_WEIGHTS = {
      smcZones: 25,
      liquidityHunter: 25,
      liquidityPsychology: 25,
      autoFib: 20,
      priceAction: 15,
      momentumSuite: 15
    };"""

repl_cfg = """    const DEFAULT_INDICATOR_CONFIG = {
      smcZones: true,        // Module 1: SMC Zones (FVG & Order Blocks) - Weight: 25
      liquidityHunter: true, // Module 2: Liquidity & Order Flow Hunter (Session Sweeps, EQH/EQL) - Weight: 25
      liquidityPsychology: true, // Dedicated: Liquidity & Candle Psychology Engine (Sweep + 5-Candle Confirmation) - Weight: 25
      dailyLiquiditySniper: true, // Dedicated: Daily Liquidity Sniper (1D Sweep + 1M Trigger) - Weight: 25
      autoFib: true,         // Module 3: Auto Fibonacci Golden Pocket (0.50 - 0.618) - Weight: 20
      priceAction: true,     // Module 4: Price Action & Candlestick Scanner - Weight: 15
      momentumSuite: false   // Module 5: Momentum & Trend Suite (EMA 20/50, RSI, MACD) - Weight: 15
    };

    const MODULE_WEIGHTS = {
      smcZones: 25,
      liquidityHunter: 25,
      liquidityPsychology: 25,
      dailyLiquiditySniper: 25,
      autoFib: 20,
      priceAction: 15,
      momentumSuite: 15
    };"""

assert target_cfg in content, "target_cfg not found in content"
content = content.replace(target_cfg, repl_cfg, 1)

# 5. Add dailyLiquiditySniperEnabled and window.daily_liquidity_sniper_active
target_vars = """    var liquidityPsychologyEnabled = !!indicatorSettings.liquidityPsychology;
    window.latestLiquidityPsychology = null;"""

repl_vars = """    var liquidityPsychologyEnabled = !!indicatorSettings.liquidityPsychology;
    window.latestLiquidityPsychology = null;
    var dailyLiquiditySniperEnabled = !!indicatorSettings.dailyLiquiditySniper;
    window.daily_liquidity_sniper_active = dailyLiquiditySniperEnabled;
    window.latestDailyLiquiditySniper = null;"""

assert target_vars in content, "target_vars not found in content"
content = content.replace(target_vars, repl_vars, 1)

# 6. Update labels in toggleModularIndicator
target_labels = """        smcZones: 'SMC Zones (OB & FVG)',
        liquidityHunter: 'Liquidity & Order Flow Hunter',
        liquidityPsychology: 'Liquidity & Candle Psychology (Sweep + Multi-Bar Confirmation)',
        autoFib: 'Auto Fibonacci Golden Pocket',"""

repl_labels = """        smcZones: 'SMC Zones (OB & FVG)',
        liquidityHunter: 'Liquidity & Order Flow Hunter',
        liquidityPsychology: 'Liquidity & Candle Psychology (Sweep + Multi-Bar Confirmation)',
        dailyLiquiditySniper: 'Daily Liquidity Sniper (PDH/PDL 1M Breakout)',
        autoFib: 'Auto Fibonacci Golden Pocket',"""

assert target_labels in content, "target_labels not found in content"
content = content.replace(target_labels, repl_labels, 1)

# 7. Update applyModularVisuals
target_visuals = """      } else if (moduleName === 'liquidityPsychology') {
        liquidityPsychologyEnabled = isChecked;
      } else if (moduleName === 'autoFib') {"""

repl_visuals = """      } else if (moduleName === 'liquidityPsychology') {
        liquidityPsychologyEnabled = isChecked;
      } else if (moduleName === 'dailyLiquiditySniper') {
        dailyLiquiditySniperEnabled = isChecked;
        window.daily_liquidity_sniper_active = isChecked;
      } else if (moduleName === 'autoFib') {"""

assert target_visuals in content, "target_visuals not found in content"
content = content.replace(target_visuals, repl_visuals, 1)

# 8. Add evaluateDailyLiquiditySniper and drawDailyLiquiditySniperOverlay functions
dls_engine_code = '''
    // ==========================================
    // DAILY LIQUIDITY SNIPER (1D SWEEP + 1M TRIGGER) ENGINE
    // State Machine: 1D PDH/PDL Sweep -> 1M Solid Red/Green Retest -> Agli Candle Low/High Breakout Trigger
    // ==========================================
    function evaluateDailyLiquiditySniper(candles, pools, currentSpot) {
      if (!candles || candles.length < 5) return null;
      if (!currentSpot) currentSpot = candles[candles.length - 1].close;

      // 1. Daily Level Tracking (PDH & PDL)
      let pdh = (pools && typeof pools.pdh === 'number' && pools.pdh > 0) ? pools.pdh : null;
      let pdl = (pools && typeof pools.pdl === 'number' && pools.pdl > 0) ? pools.pdl : null;

      if (!pdh || !pdl) {
        const curBar = candles[candles.length - 1];
        const curUtcDate = new Date(curBar.time * 1000).toISOString().slice(0, 10);
        let prevUtcDate = null;
        for (let i = candles.length - 1; i >= 0; i--) {
          const dStr = new Date(candles[i].time * 1000).toISOString().slice(0, 10);
          if (dStr < curUtcDate) {
            prevUtcDate = dStr;
            break;
          }
        }
        if (prevUtcDate) {
          const prevDayCandles = candles.filter(c => new Date(c.time * 1000).toISOString().slice(0, 10) === prevUtcDate);
          if (prevDayCandles.length > 0) {
            pdh = Math.max(...prevDayCandles.map(c => c.high));
            pdl = Math.min(...prevDayCandles.map(c => c.low));
          }
        }
        if (!pdh || !pdl) {
          const slice = candles.slice(-96, -24);
          if (slice.length >= 10) {
            pdh = Math.max(...slice.map(c => c.high));
            pdl = Math.min(...slice.map(c => c.low));
          } else {
            pdh = Math.max(...candles.slice(-48, -12).map(c => c.high));
            pdl = Math.min(...candles.slice(-48, -12).map(c => c.low));
          }
        }
      }

      pdh = Number(pdh.toFixed(2));
      pdl = Number(pdl.toFixed(2));

      // 2. Obtain 1M execution candles (Direct 1M or Resampled from 15M/5M)
      let c1m = null;
      if (candles && (typeof currentTf !== 'undefined' && currentTf === '1m' || candles.length <= 30 || !window.mtfCandleStore || !window.mtfCandleStore['1m'])) {
        c1m = candles;
      } else if (window.mtfCandleStore && window.mtfCandleStore['1m'] && window.mtfCandleStore['1m'].length >= 10) {
        c1m = window.mtfCandleStore['1m'];
      } else if (typeof resampleCandles === 'function') {
        const curSec = (typeof currentTf !== 'undefined' && currentTf === '5m') ? 300 : ((typeof currentTf !== 'undefined' && currentTf === '1h') ? 3600 : ((typeof currentTf !== 'undefined' && currentTf === '4h') ? 14400 : 900));
        c1m = resampleCandles(candles, curSec, 60);
      } else {
        c1m = candles;
      }

      if (!c1m || c1m.length < 5) return null;

      // 3. 1-Minute Micro-Execution State Machine
      const lookback = Math.min(30, c1m.length - 2);
      const startIdx = Math.max(1, c1m.length - lookback);

      let latestShortSetup = null;
      let latestBuySetup = null;

      for (let i = startIdx; i < c1m.length - 1; i++) {
        const bar = c1m[i];
        const nextBar = c1m[i + 1];

        // --- SHORT / SELL SETUP ---
        // State 1: 1M price breaks above PDH (high >= PDH)
        // State 2: A solid red candle closes above or retesting the PDH level
        const isRedCandle = bar.close < bar.open;
        const sweepsPdh = bar.high >= pdh;
        const retestsPdh = (bar.close >= (pdh - 1.20) || bar.open >= pdh);

        if (sweepsPdh && isRedCandle && retestsPdh) {
          // State 3: Next 1M candle breaks strictly below the LOW of that red candle
          if (nextBar.low < bar.low) {
            const redHigh = bar.high;
            const sl = Number((redHigh + 0.50).toFixed(2));
            let invalidated = false;
            for (let k = i + 1; k < c1m.length; k++) {
              if (c1m[k].high > sl) {
                invalidated = true;
                break;
              }
            }

            if (!invalidated) {
              const entry = Number(nextBar.close.toFixed(2));
              const risk = Math.max(0.80, sl - entry);

              // TP1: Recent swing low prior to rally (Min 1:4.0 RR)
              const preSlice = c1m.slice(Math.max(0, i - 20), i);
              let recentSwingLow = preSlice.length ? Math.min(...preSlice.map(b => b.low)) : (entry - (risk * 4.0));
              if ((entry - recentSwingLow) / risk < 4.0) {
                recentSwingLow = entry - (risk * 4.0);
              }
              const tp1 = Number(recentSwingLow.toFixed(2));
              // TP2: 1:10 RR Target
              const tp2 = Number((entry - (risk * 10.0)).toFixed(2));
              const gainPts = Number((entry - tp1).toFixed(1));
              const rrRatio = (gainPts / risk).toFixed(1);

              latestShortSetup = {
                active: true,
                direction: "SELL",
                type: "SELL",
                action: "HIGH CONVICTION SELL",
                confidence: "96% (PDH Swept + 1M Red Low Purged)",
                badge: "⚡ DLS-1M SNIPER",
                pdh,
                pdl,
                sweepLevel: pdh,
                sweepLevelName: "PDH",
                redCandle: bar,
                triggerBar: nextBar,
                triggerIndex: i + 1,
                entry,
                sl,
                tp1,
                tp2,
                tp: tp1,
                risk,
                gainPts,
                rr: `1 : ${rrRatio} (TP1) · 1 : 10.0 (TP2)`,
                rrText: `1 : ${rrRatio} (+${gainPts} pts)`,
                reason: "Confirmed: PDH Swept + 1M Red Candle Low Purged (Sellers Dominated)"
              };
            }
          }
        }

        // --- BUY / LONG SETUP ---
        // State 1: 1M price drops below PDL (low <= PDL)
        // State 2: A solid green candle closes below or retesting the PDL level
        const isGreenCandle = bar.close > bar.open;
        const sweepsPdl = bar.low <= pdl;
        const retestsPdl = (bar.close <= (pdl + 1.20) || bar.open <= pdl);

        if (sweepsPdl && isGreenCandle && retestsPdl) {
          // State 3: Next 1M candle breaks strictly above the HIGH of that green candle
          if (nextBar.high > bar.high) {
            const greenLow = bar.low;
            const sl = Number((greenLow - 0.50).toFixed(2));
            let invalidated = false;
            for (let k = i + 1; k < c1m.length; k++) {
              if (c1m[k].low < sl) {
                invalidated = true;
                break;
              }
            }

            if (!invalidated) {
              const entry = Number(nextBar.close.toFixed(2));
              const risk = Math.max(0.80, entry - sl);

              // TP1: Recent swing high prior to dump (Min 1:4.0 RR)
              const preSlice = c1m.slice(Math.max(0, i - 20), i);
              let recentSwingHigh = preSlice.length ? Math.max(...preSlice.map(b => b.high)) : (entry + (risk * 4.0));
              if ((recentSwingHigh - entry) / risk < 4.0) {
                recentSwingHigh = entry + (risk * 4.0);
              }
              const tp1 = Number(recentSwingHigh.toFixed(2));
              // TP2: 1:10 RR Target
              const tp2 = Number((entry + (risk * 10.0)).toFixed(2));
              const gainPts = Number((tp1 - entry).toFixed(1));
              const rrRatio = (gainPts / risk).toFixed(1);

              latestBuySetup = {
                active: true,
                direction: "BUY",
                type: "BUY",
                action: "HIGH CONVICTION BUY",
                confidence: "96% (PDL Swept + 1M Green High Purged)",
                badge: "⚡ DLS-1M SNIPER",
                pdh,
                pdl,
                sweepLevel: pdl,
                sweepLevelName: "PDL",
                greenCandle: bar,
                triggerBar: nextBar,
                triggerIndex: i + 1,
                entry,
                sl,
                tp1,
                tp2,
                tp: tp1,
                risk,
                gainPts,
                rr: `1 : ${rrRatio} (TP1) · 1 : 10.0 (TP2)`,
                rrText: `1 : ${rrRatio} (+${gainPts} pts)`,
                reason: "Confirmed: PDL Swept + 1M Green Candle High Purged (Buyers Dominated)"
              };
            }
          }
        }
      }

      if (latestShortSetup && latestBuySetup) {
        return (latestShortSetup.triggerIndex >= latestBuySetup.triggerIndex) ? latestShortSetup : latestBuySetup;
      }
      if (latestShortSetup) return latestShortSetup;
      if (latestBuySetup) return latestBuySetup;

      // Mid-Range Standby Filter (No Trade Zone)
      return {
        active: false,
        isStandby: true,
        direction: "STANDBY",
        action: "STANDBY: PRICE IN MID-RANGE",
        confidence: "PDH/PDL Boundary Scanner Active",
        badge: "⚡ DLS-1M SNIPER",
        pdh,
        pdl,
        currentSpot,
        entry: currentSpot,
        sl: 0,
        tp1: 0,
        tp2: 0,
        risk: 0,
        gainPts: 0,
        rr: "0 : 0 (NO TRADE)",
        rrText: "0 : 0 (NO TRADE)",
        reason: `Standby: Price floating in Mid-Range between PDH ($${pdh.toFixed(2)}) and PDL ($${pdl.toFixed(2)}) - No Trade Zone. Waiting for boundary sweep.`
      };
    }
    window.evaluateDailyLiquiditySniper = evaluateDailyLiquiditySniper;

    // Dedicated Canvas Overlay for Daily Reference Lines (PDH Golden, PDL Cyan)
    function drawDailyLiquiditySniperOverlay(ctx, dlsResult, pools) {
      if (!ctx || !candleSeries || !chart) return;
      if (typeof indicatorSettings !== 'undefined' && !indicatorSettings.dailyLiquiditySniper) return;

      let pdh = dlsResult ? dlsResult.pdh : (pools ? pools.pdh : null);
      let pdl = dlsResult ? dlsResult.pdl : (pools ? pools.pdl : null);
      if (!pdh || !pdl) return;

      const yPdh = candleSeries.priceToCoordinate(pdh);
      const yPdl = candleSeries.priceToCoordinate(pdl);

      ctx.save();

      // 1. Golden Reference Line at PDH
      if (yPdh !== null && yPdh >= 10 && yPdh <= canvasCssHeight - 15) {
        const isSwept = dlsResult && dlsResult.active && dlsResult.direction === 'SELL';
        ctx.strokeStyle = '#ffd700';
        ctx.lineWidth = isSwept ? 1.8 : 1.0;
        ctx.setLineDash(isSwept ? [6, 3] : [5, 4]);
        if (isSwept) {
          ctx.shadowColor = 'rgba(255, 215, 0, 0.7)';
          ctx.shadowBlur = 6;
        } else {
          ctx.shadowBlur = 0;
        }

        ctx.beginPath();
        ctx.moveTo(15, yPdh);
        ctx.lineTo(canvasCssWidth - 65, yPdh);
        ctx.stroke();
        ctx.setLineDash([]);
        ctx.shadowBlur = 0;

        const tagText = isSwept ? `⚡ PDH SWEPT · $${pdh.toFixed(2)} [1M SHORT TRIGGERED]` : `PDH (Liquidity High) · $${pdh.toFixed(2)}`;
        ctx.font = '700 9px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace';
        const tw = ctx.measureText(tagText).width;
        const bw = Math.round(tw + 12);
        const bh = 16;
        const bx = canvasCssWidth - bw - 72;
        const by = Math.round(yPdh - bh / 2);

        ctx.fillStyle = 'rgba(10, 18, 28, 0.94)';
        ctx.fillRect(bx, by, bw, bh);
        ctx.strokeStyle = '#ffd700';
        ctx.lineWidth = 1;
        ctx.strokeRect(bx, by, bw, bh);
        ctx.fillStyle = '#ffd700';
        ctx.textBaseline = 'middle';
        ctx.fillText(tagText, bx + 6, yPdh);
      }

      // 2. Cyan Reference Line at PDL
      if (yPdl !== null && yPdl >= 10 && yPdl <= canvasCssHeight - 15) {
        const isSwept = dlsResult && dlsResult.active && dlsResult.direction === 'BUY';
        ctx.strokeStyle = '#00e5ff';
        ctx.lineWidth = isSwept ? 1.8 : 1.0;
        ctx.setLineDash(isSwept ? [6, 3] : [5, 4]);
        if (isSwept) {
          ctx.shadowColor = 'rgba(0, 229, 255, 0.7)';
          ctx.shadowBlur = 6;
        } else {
          ctx.shadowBlur = 0;
        }

        ctx.beginPath();
        ctx.moveTo(15, yPdl);
        ctx.lineTo(canvasCssWidth - 65, yPdl);
        ctx.stroke();
        ctx.setLineDash([]);
        ctx.shadowBlur = 0;

        const tagText = isSwept ? `⚡ PDL SWEPT · $${pdl.toFixed(2)} [1M BUY TRIGGERED]` : `PDL (Liquidity Low) · $${pdl.toFixed(2)}`;
        ctx.font = '700 9px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace';
        const tw = ctx.measureText(tagText).width;
        const bw = Math.round(tw + 12);
        const bh = 16;
        const bx = canvasCssWidth - bw - 72;
        const by = Math.round(yPdl - bh / 2);

        ctx.fillStyle = 'rgba(10, 18, 28, 0.94)';
        ctx.fillRect(bx, by, bw, bh);
        ctx.strokeStyle = '#00e5ff';
        ctx.lineWidth = 1;
        ctx.strokeRect(bx, by, bw, bh);
        ctx.fillStyle = '#00e5ff';
        ctx.textBaseline = 'middle';
        ctx.fillText(tagText, bx + 6, yPdl);
      }

      ctx.restore();
    }
    window.drawDailyLiquiditySniperOverlay = drawDailyLiquiditySniperOverlay;
'''

target_scan = "    window.scanAllLiquidityPsychology = scanAllLiquidityPsychology;"
repl_scan = target_scan + "\n" + dls_engine_code

assert target_scan in content, "target_scan not found in content"
content = content.replace(target_scan, repl_scan, 1)

# 9. Update redrawDrawings to call drawDailyLiquiditySniperOverlay and Risk/Reward overlay
target_draw_liq_psy = """      // 2.2 Dedicated: Liquidity & Candle Psychology Engine Overlay
      if (typeof indicatorSettings !== 'undefined' && indicatorSettings.liquidityPsychology) {
        const actPools = (typeof currentLiquidityPools !== 'undefined' && currentLiquidityPools) ? currentLiquidityPools : (window.currentLiquidityPools || null);
        drawLiquidityPsychologyOverlay(drawingCtx, window.latestLiquidityPsychology, actPools);
      }"""

repl_draw_liq_psy = target_draw_liq_psy + """

      // 2.3 Dedicated: Daily Liquidity Sniper Reference Lines (Golden PDH, Cyan PDL)
      if (typeof indicatorSettings !== 'undefined' && indicatorSettings.dailyLiquiditySniper) {
        const actPools = (typeof currentLiquidityPools !== 'undefined' && currentLiquidityPools) ? currentLiquidityPools : (window.currentLiquidityPools || null);
        drawDailyLiquiditySniperOverlay(drawingCtx, window.latestDailyLiquiditySniper, actPools);
      }"""

assert target_draw_liq_psy in content, "target_draw_liq_psy not found in content"
content = content.replace(target_draw_liq_psy, repl_draw_liq_psy, 1)

# 10. Update showRROverlay check for dailyLiquiditySniper
target_rr_check = """      // 3. Automatic Risk/Reward Position Tool (Short/Long Tool)
      if (showRROverlay) {
        if (typeof indicatorSettings !== 'undefined' && indicatorSettings.liquidityPsychology && window.latestLiquidityPsychology) {"""

repl_rr_check = """      // 3. Automatic Risk/Reward Position Tool (Short/Long Tool)
      if (showRROverlay) {
        if (typeof indicatorSettings !== 'undefined' && indicatorSettings.dailyLiquiditySniper && window.latestDailyLiquiditySniper && window.latestDailyLiquiditySniper.active) {
          const dls = window.latestDailyLiquiditySniper;
          const riskPts = Math.abs(Number(dls.entry) - Number(dls.sl));
          const rewardPts = Math.abs(Number(dls.tp1) - Number(dls.entry));
          const rrRatio = (rewardPts / Math.max(0.1, riskPts)).toFixed(1);
          drawRiskRewardOverlay(drawingCtx, {
            type: dls.direction === 'BUY' ? 'LONG' : 'SHORT',
            entry: Number(dls.entry),
            sl: Number(dls.sl),
            tp: Number(dls.tp1),
            risk: riskPts,
            reward: rewardPts,
            rrRatio: rrRatio
          });
        } else if (typeof indicatorSettings !== 'undefined' && indicatorSettings.liquidityPsychology && window.latestLiquidityPsychology) {"""

assert target_rr_check in content, "target_rr_check not found in content"
content = content.replace(target_rr_check, repl_rr_check, 1)

# 11. Add evaluateDailyLiquiditySniper call in evaluateHighAccuracySetup
target_eval_psy = """      // 0.2 DEDICATED: LIQUIDITY & CANDLE PSYCHOLOGY ENGINE EVALUATION
      const activePsychology = (typeof indicatorSettings !== 'undefined' && indicatorSettings.liquidityPsychology)
        ? scanAllLiquidityPsychology(candles, currentLiquidityPools)
        : null;
      window.latestLiquidityPsychology = activePsychology;"""

repl_eval_psy = target_eval_psy + """

      // 0.3 DEDICATED: DAILY LIQUIDITY SNIPER (1D SWEEP + 1M TRIGGER)
      const activeDLS = (typeof indicatorSettings !== 'undefined' && indicatorSettings.dailyLiquiditySniper)
        ? evaluateDailyLiquiditySniper(candles, currentLiquidityPools, currentPrice)
        : null;
      window.latestDailyLiquiditySniper = activeDLS;"""

assert target_eval_psy in content, "target_eval_psy not found in content"
content = content.replace(target_eval_psy, repl_eval_psy, 1)

# 12. Add evaluateDailyLiquiditySniperModule and update evaluateActiveConfluence
target_confluence_func = """    function evaluateLiquidityPsychologyModule(candles, currentSpot, liquidityPools) {
      if (window.latestLiquidityPsychology) {
        const psy = window.latestLiquidityPsychology;
        return {
          bias: psy.type === 'BUY' ? 'BUY' : 'SELL',
          score: 25,
          reason: psy.reason,
          summary: `${psy.levelCode || 'Pool'} Absorbed`
        };
      }
      return {
        bias: 'NEUTRAL',
        score: 0,
        reason: 'Scanning liquidity pools for 5-bar confirmation',
        summary: 'Scanning'
      };
    }"""

repl_confluence_func = target_confluence_func + """

    function evaluateDailyLiquiditySniperModule(candles, currentSpot, liquidityPools) {
      if (window.latestDailyLiquiditySniper) {
        const dls = window.latestDailyLiquiditySniper;
        if (dls.active) {
          return {
            bias: dls.direction,
            score: 25,
            reason: dls.reason,
            summary: `${dls.direction} Confirmed`
          };
        } else if (dls.isStandby) {
          return {
            bias: 'NEUTRAL',
            score: 0,
            reason: dls.reason,
            summary: 'Mid-Range Standby'
          };
        }
      }
      return {
        bias: 'NEUTRAL',
        score: 0,
        reason: 'Scanning PDH/PDL 1M Breakouts',
        summary: 'Scanning'
      };
    }"""

assert target_confluence_func in content, "target_confluence_func not found in content"
content = content.replace(target_confluence_func, repl_confluence_func, 1)

# In evaluateActiveConfluence, invoke module and register in modules object
target_act_conf = """      const liqPsyRes = evaluateLiquidityPsychologyModule(candles, spot, liquidityPools);
      const fibRes = evaluateAutoFibModule(candles, spot);"""

repl_act_conf = """      const liqPsyRes = evaluateLiquidityPsychologyModule(candles, spot, liquidityPools);
      const dlsRes = evaluateDailyLiquiditySniperModule(candles, spot, liquidityPools);
      const fibRes = evaluateAutoFibModule(candles, spot);"""

assert target_act_conf in content, "target_act_conf not found in content"
content = content.replace(target_act_conf, repl_act_conf, 1)

target_modules = """        liquidityPsychology: { name: 'Liquidity & Candle Psychology', weight: 25, active: !!indicatorSettings.liquidityPsychology, result: liqPsyRes },
        autoFib: { name: 'Auto Fib Golden Pocket', weight: 20, active: !!indicatorSettings.autoFib, result: fibRes },"""

repl_modules = """        liquidityPsychology: { name: 'Liquidity & Candle Psychology', weight: 25, active: !!indicatorSettings.liquidityPsychology, result: liqPsyRes },
        dailyLiquiditySniper: { name: 'Daily Liquidity Sniper', weight: 25, active: !!indicatorSettings.dailyLiquiditySniper, result: dlsRes },
        autoFib: { name: 'Auto Fib Golden Pocket', weight: 20, active: !!indicatorSettings.autoFib, result: fibRes },"""

assert target_modules in content, "target_modules not found in content"
content = content.replace(target_modules, repl_modules, 1)

# 13. In updateActiveSetupCard: Set Priority 0 for dailyLiquiditySniper driving the EXECUTION SIGNALS card
target_card_priority = """      // 0. REAL-TIME INSTITUTIONAL LIQUIDITY SWEEP PRIORITY UPDATE
      const curLock = (typeof shortTermSignalLock !== 'undefined' && shortTermSignalLock) 
        ? shortTermSignalLock 
        : (window.shortTermSignalLock || null);

      if (typeof indicatorSettings !== 'undefined' && indicatorSettings.liquidityPsychology && window.latestLiquidityPsychology && (!curLock || !curLock.active || curLock.status !== 'ACTIVE_HOLD' || curLock.reason !== window.latestLiquidityPsychology.reason)) {"""

repl_card_priority = """      // 0. PRIORITY 0: REAL-TIME DAILY LIQUIDITY SNIPER (1D SWEEP + 1M TRIGGER)
      const curLock = (typeof shortTermSignalLock !== 'undefined' && shortTermSignalLock) 
        ? shortTermSignalLock 
        : (window.shortTermSignalLock || null);

      if (typeof indicatorSettings !== 'undefined' && indicatorSettings.dailyLiquiditySniper && window.latestDailyLiquiditySniper) {
        const dls = window.latestDailyLiquiditySniper;
        if (dls.active) {
          if (!curLock || !curLock.active || curLock.status !== 'ACTIVE_HOLD' || curLock.reason !== dls.reason || curLock.signalType !== dls.direction) {
            shortTermSignalLock = {
              active: true,
              signalType: dls.direction,
              action: dls.direction === 'BUY' ? 'HIGH CONVICTION BUY' : 'HIGH CONVICTION SELL',
              confidence: dls.confidence || '96% (DLS-1M Micro Breakout Verified)',
              entryPrice: dls.entry,
              tp1: dls.tp1,
              tp2: dls.tp2,
              sl: Number(dls.sl),
              rr: dls.rr,
              rrText: dls.rrText,
              gainPts: dls.gainPts,
              reason: dls.reason,
              badgeText: dls.badge || '⚡ DLS-1M SNIPER',
              lockedAt: now,
              maxLockDurationMs: 60 * 60 * 1000,
              status: 'ACTIVE_HOLD',
              completedAt: null,
              lastCompletedType: curLock ? curLock.lastCompletedType : null,
              lastCompletedStatus: curLock ? curLock.lastCompletedStatus : null
            };
            window.shortTermSignalLock = shortTermSignalLock;
          }
        } else if (dls.isStandby) {
          if (!curLock || !curLock.active || curLock.status !== 'ACTIVE_HOLD' || curLock.status === 'STANDBY_MIDRANGE') {
            shortTermSignalLock = {
              active: false,
              signalType: 'STANDBY',
              action: 'STANDBY: PRICE IN MID-RANGE',
              confidence: 'PDH/PDL Boundary Scan Active (No-Trade Zone)',
              entryPrice: currentSpot,
              tp1: currentSpot,
              tp2: currentSpot,
              sl: 0,
              rr: '0 : 0 (STANDBY)',
              rrText: '0 : 0 (STANDBY)',
              gainPts: 0,
              reason: dls.reason,
              badgeText: '⚡ DLS-1M SNIPER (STANDBY)',
              lockedAt: now,
              maxLockDurationMs: 60 * 60 * 1000,
              status: 'STANDBY_MIDRANGE',
              completedAt: null,
              lastCompletedType: curLock ? curLock.lastCompletedType : null,
              lastCompletedStatus: curLock ? curLock.lastCompletedStatus : null
            };
            window.shortTermSignalLock = shortTermSignalLock;
          }
        }
      } else if (typeof indicatorSettings !== 'undefined' && indicatorSettings.liquidityPsychology && window.latestLiquidityPsychology && (!curLock || !curLock.active || curLock.status !== 'ACTIVE_HOLD' || curLock.reason !== window.latestLiquidityPsychology.reason)) {"""

assert target_card_priority in content, "target_card_priority not found in content"
content = content.replace(target_card_priority, repl_card_priority, 1)

# 14. Update stDirPill for STANDBY_MIDRANGE
target_dir_pill = """        } else if (shortTermSignalLock.status === 'CONFLICT_HOLD') {
          stDirPill.innerText = 'STANDBY ⚠️';
          stDirPill.className = 'exec-dir-pill standby';
          stDirPill.style.background = 'rgba(234, 179, 8, 0.2)';
          stDirPill.style.color = '#eab308';
          stDirPill.style.borderColor = 'rgba(234, 179, 8, 0.5)';"""

repl_dir_pill = """        } else if (shortTermSignalLock.status === 'CONFLICT_HOLD' || shortTermSignalLock.status === 'STANDBY_MIDRANGE') {
          stDirPill.innerText = 'STANDBY ⚠️';
          stDirPill.className = 'exec-dir-pill standby';
          stDirPill.style.background = 'rgba(234, 179, 8, 0.2)';
          stDirPill.style.color = '#eab308';
          stDirPill.style.borderColor = 'rgba(234, 179, 8, 0.5)';"""

assert target_dir_pill in content, "target_dir_pill not found in content"
content = content.replace(target_dir_pill, repl_dir_pill, 1)

# 15. Update stModularPipelineGrid in updateActiveSetupCard
target_pipe_updates = """        updateStep('pipeLiq', 'liquidityHunter', '💧 Liq');
        updateStep('pipeLiqPsy', 'liquidityPsychology', '⚡ Liq Psy');
        updateStep('pipeFib', 'autoFib', '🎯 Fib');"""

repl_pipe_updates = """        updateStep('pipeLiq', 'liquidityHunter', '💧 Liq');
        updateStep('pipeLiqPsy', 'liquidityPsychology', '⚡ Liq Psy');
        updateStep('pipeDLS', 'dailyLiquiditySniper', '⚡ DLS-1M');
        updateStep('pipeFib', 'autoFib', '🎯 Fib');"""

assert target_pipe_updates in content, "target_pipe_updates not found in content"
content = content.replace(target_pipe_updates, repl_pipe_updates, 1)

# 16. Update stEntry, stSl, stTp for STANDBY_MIDRANGE
target_entry_sl = """      if (shortTermSignalLock.status === 'SL_HIT') {
        if (stEntry) { stEntry.innerText = 'INVALIDATED'; stEntry.style.color = '#8b949e'; }
        if (stSl) { stSl.innerText = '$' + shortTermSignalLock.sl.toFixed(2) + ' (HIT)'; stSl.style.color = '#f85149'; }
        if (stTp) { stTp.innerText = 'CANCELLED'; stTp.style.color = '#8b949e'; }
        if (stRr) stRr.innerText = '0 : 0 (STOPPED)';
      } else {"""

repl_entry_sl = """      if (shortTermSignalLock.status === 'SL_HIT') {
        if (stEntry) { stEntry.innerText = 'INVALIDATED'; stEntry.style.color = '#8b949e'; }
        if (stSl) { stSl.innerText = '$' + shortTermSignalLock.sl.toFixed(2) + ' (HIT)'; stSl.style.color = '#f85149'; }
        if (stTp) { stTp.innerText = 'CANCELLED'; stTp.style.color = '#8b949e'; }
        if (stRr) stRr.innerText = '0 : 0 (STOPPED)';
      } else if (shortTermSignalLock.status === 'STANDBY_MIDRANGE') {
        if (stEntry) { stEntry.innerText = '$' + currentSpot.toFixed(2); stEntry.style.color = '#8b949e'; }
        if (stSl) { stSl.innerText = 'NO TRADE ZONE'; stSl.style.color = '#eab308'; }
        if (stTp) { stTp.innerText = 'WAITING BOUNDARY'; stTp.style.color = '#8b949e'; }
        if (stRr) stRr.innerText = '0 : 0 (STANDBY)';
      } else {"""

assert target_entry_sl in content, "target_entry_sl not found in content"
content = content.replace(target_entry_sl, repl_entry_sl, 1)

# 17. Update stLiquidityBadge for dailyLiquiditySniper
target_liq_badge = """      // Update 1-Line Liquidity Sweep Confirmation Badge
      const stLiqBadge = document.getElementById('stLiquidityBadge');
      if (stLiqBadge) {
        const currentLock = (typeof shortTermSignalLock !== 'undefined' && shortTermSignalLock) ? shortTermSignalLock : window.shortTermSignalLock;
        if (window.latestLiquidityPsychology && currentLock && (currentLock.status === 'ACTIVE_HOLD' || currentLock.status === 'RUNNER_ACTIVE')) {"""

repl_liq_badge = """      // Update 1-Line Liquidity Sweep Confirmation Badge
      const stLiqBadge = document.getElementById('stLiquidityBadge');
      if (stLiqBadge) {
        const currentLock = (typeof shortTermSignalLock !== 'undefined' && shortTermSignalLock) ? shortTermSignalLock : window.shortTermSignalLock;
        if (window.latestDailyLiquiditySniper && indicatorSettings && indicatorSettings.dailyLiquiditySniper) {
          const dls = window.latestDailyLiquiditySniper;
          if (dls.active) {
            stLiqBadge.innerText = `⚡ DLS-1M SNIPER (${dls.direction} CONFIRMED)`;
            stLiqBadge.style.display = 'block';
            stLiqBadge.style.background = dls.direction === 'BUY' ? 'rgba(46, 160, 67, 0.15)' : 'rgba(248, 81, 73, 0.15)';
            stLiqBadge.style.color = dls.direction === 'BUY' ? '#3fb950' : '#f85149';
            stLiqBadge.style.borderColor = dls.direction === 'BUY' ? 'rgba(46, 160, 67, 0.4)' : 'rgba(248, 81, 73, 0.4)';
          } else if (dls.isStandby) {
            stLiqBadge.innerText = `⚡ DLS-1M SNIPER (MID-RANGE NO-TRADE ZONE)`;
            stLiqBadge.style.display = 'block';
            stLiqBadge.style.background = 'rgba(234, 179, 8, 0.12)';
            stLiqBadge.style.color = '#eab308';
            stLiqBadge.style.borderColor = 'rgba(234, 179, 8, 0.35)';
          } else {
            stLiqBadge.style.display = 'none';
          }
        } else if (window.latestLiquidityPsychology && currentLock && (currentLock.status === 'ACTIVE_HOLD' || currentLock.status === 'RUNNER_ACTIVE')) {"""

assert target_liq_badge in content, "target_liq_badge not found in content"
content = content.replace(target_liq_badge, repl_liq_badge, 1)

# Write back to gold_dashboard.html, deep_analysis_gold.html, index.html
with open('gold_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)

with open('deep_analysis_gold.html', 'w', encoding='utf-8') as f:
    f.write(content)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Successfully applied Daily Liquidity Sniper indicator across all 3 dashboard files!')
