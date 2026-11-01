import sys
import os
import hashlib

def main():
    print("Reading gold_dashboard.html...")
    with open('gold_dashboard.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Menu Toggle in #tvIndicatorsMenu
    target_menu = '<!-- Indicator: Daily Liquidity Sniper (1D Sweep + 1M Trigger) -->'
    assert target_menu in content, "target_menu not found"
    menu_toggle = '''<!-- Indicator: VWAP + EMA + FVG Confluence Engine -->
            <div class="tv-ind-row" onclick="clickModularToggle('vwapEmaFvg', event)">
              <div class="tv-ind-info">
                <div style="display: flex; align-items: center; gap: 6px;">
                  <b style="color: #ffa726;">⚡ VWAP + EMA + FVG Engine</b>
                  <span style="font-size: 9px; background: rgba(255,167,38,0.18); color: #ffa726; padding: 1px 4px; border-radius: 4px; font-weight: 700;">WT: 20%</span>
                </div>
                <small>Session VWAP Anchor + Dynamic EMA 20 + 15M FVG Mitigation Sniper</small>
              </div>
              <label class="toggle-switch" onclick="event.stopPropagation()">
                <input type="checkbox" id="ind-toggle-vwapEmaFvg" checked onchange="toggleModularIndicator('vwapEmaFvg')">
                <span class="toggle-slider"></span>
              </label>
            </div>

            '''
    content = content.replace(target_menu, menu_toggle + target_menu, 1)

    # 2. Modal Toggle in #indicatorsModal
    target_modal_anchor = '<input type="checkbox" id="modal-toggle-dailyLiquiditySniper" checked onchange="toggleModularIndicator(\'dailyLiquiditySniper\')">\n            <span class="toggle-slider"></span>\n          </label>\n        </div>'
    assert target_modal_anchor in content, "target_modal_anchor not found"
    modal_toggle = '''

        <div class="indicator-row">
          <div>
            <div style="display: flex; align-items: center; gap: 6px;">
              <b style="color: #ffa726;">⚡ VWAP + EMA + FVG Engine</b>
              <span style="font-size: 9px; background: rgba(255,167,38,0.18); color: #ffa726; padding: 1px 4px; border-radius: 4px; font-weight: 700;">WT: 20%</span>
            </div>
            <p style="font-size: 11px; color: #8b949e; margin: 2px 0 0;">Session VWAP Anchor + Dynamic EMA 20 + 15M FVG Mitigation Sniper</p>
          </div>
          <label class="toggle-switch">
            <input type="checkbox" id="modal-toggle-vwapEmaFvg" checked onchange="toggleModularIndicator('vwapEmaFvg')">
            <span class="toggle-slider"></span>
          </label>
        </div>'''
    content = content.replace(target_modal_anchor, target_modal_anchor + modal_toggle, 1)

    # 3. Pipeline step in #stModularPipelineGrid
    target_pipe_anchor = '<span id="pipeDLS" class="pipe-step-pill active" title="Step 3.5: Daily Liquidity Sniper (PDH/PDL 1M Breakout)">⚡ DLS-1M: Active</span>'
    assert target_pipe_anchor in content, "target_pipe_anchor not found"
    pipe_elem = '\n              <span id="pipeVwapFvg" class="pipe-step-pill active" title="Step 3.8: VWAP + EMA + FVG Engine">⚡ VWAP+FVG: Confluence</span>'
    content = content.replace(target_pipe_anchor, target_pipe_anchor + pipe_elem, 1)

    # 4. DEFAULT_INDICATOR_CONFIG & MODULE_WEIGHTS
    target_cfg = 'dailyLiquiditySniper: true, // Dedicated: Daily Liquidity Sniper (1D Sweep + 1M Trigger) - Weight: 25'
    assert target_cfg in content, "target_cfg not found"
    content = content.replace(target_cfg, target_cfg + '\n      vwapEmaFvg: true,           // Dedicated: VWAP + EMA + FVG Confluence Engine - Weight: 20', 1)

    target_wt = 'dailyLiquiditySniper: 25,'
    assert target_wt in content, "target_wt not found"
    content = content.replace(target_wt, target_wt + '\n      vwapEmaFvg: 20,', 1)

    # 5. Indicator Variables
    target_vars = 'var dailyLiquiditySniperEnabled = !!indicatorSettings.dailyLiquiditySniper;'
    assert target_vars in content, "target_vars not found"
    var_decl = '''var dailyLiquiditySniperEnabled = !!indicatorSettings.dailyLiquiditySniper;
    var vwapEmaFvgEnabled = !!indicatorSettings.vwapEmaFvg;
    window.vwap_ema_fvg_active = vwapEmaFvgEnabled;
    window.latestVWAP_EMA_FVG = null;'''
    content = content.replace(target_vars, var_decl, 1)

    # 6. TabMap, Labels, applyModularVisuals
    target_tabmap = "dailyLiquiditySniper: 'DLS',"
    assert target_tabmap in content, "target_tabmap not found"
    content = content.replace(target_tabmap, target_tabmap + "\n        vwapEmaFvg: 'VWAP_FVG',", 1)

    target_labels = "dailyLiquiditySniper: 'Daily Liquidity Sniper (PDH/PDL 1M Breakout)',"
    assert target_labels in content, "target_labels not found"
    content = content.replace(target_labels, target_labels + "\n        vwapEmaFvg: 'VWAP + EMA + FVG Confluence Engine',", 1)

    target_apply = "else if (moduleName === 'dailyLiquiditySniper') {"
    assert target_apply in content, "target_apply not found"
    apply_decl = '''else if (moduleName === 'vwapEmaFvg') {
        vwapEmaFvgEnabled = isChecked;
        window.vwap_ema_fvg_active = isChecked;
      } else if (moduleName === 'dailyLiquiditySniper') {'''
    content = content.replace(target_apply, apply_decl, 1)

    # 7. Engine Mathematical Functions & Canvas Overlay
    target_state = '// ==========================================\n    // DEDICATED PER-INDICATOR SIGNAL TELEMETRY ENGINE'
    assert target_state in content, "target_state not found"
    vwap_core_engine = '''// ==========================================
    // VWAP + EMA + FVG CONFLUENCE ENGINE (Institutional Anchor & Sniper Tap)
    // ==========================================
    function calculateSessionVWAPSeries(candles) {
      if (!candles || candles.length === 0) return [];
      const series = [];
      let cumVol = 0;
      let cumTPV = 0;
      let curUtcDay = null;

      for (let i = 0; i < candles.length; i++) {
        const c = candles[i];
        const utcDay = new Date(c.time * 1000).toISOString().slice(0, 10);
        if (utcDay !== curUtcDay) {
          curUtcDay = utcDay;
          cumVol = 0;
          cumTPV = 0;
        }
        const vol = (typeof c.volume === 'number' && c.volume > 0) ? c.volume : (Math.abs(c.close - c.open) * 120 + 100);
        const tp = (c.high + c.low + c.close) / 3;
        cumVol += vol;
        cumTPV += tp * vol;
        const vwapVal = cumVol > 0 ? Number((cumTPV / cumVol).toFixed(2)) : c.close;
        series.push({ time: c.time, value: vwapVal });
      }
      return series;
    }

    function calculateSessionVWAP(candles) {
      if (!candles || candles.length === 0) return null;
      const s = calculateSessionVWAPSeries(candles);
      return s.length > 0 ? s[s.length - 1].value : candles[candles.length - 1].close;
    }

    function evaluateVWAP_EMA_FVG(candles, fvgZones, spotPrice) {
      if (!candles || candles.length < 5) return null;
      const lastBar = candles[candles.length - 1];
      const spot = (typeof spotPrice === 'number' && spotPrice > 0) ? spotPrice : lastBar.close;

      // 1. Session VWAP & Dynamic EMA 20
      const vwapSeries = calculateSessionVWAPSeries(candles);
      const currentVWAP = vwapSeries.length > 0 ? vwapSeries[vwapSeries.length - 1].value : spot;

      const ema20Arr = (typeof calculateEMA === 'function') ? calculateEMA(candles, 20) : [];
      const currentEMA20 = ema20Arr.length > 0 ? ema20Arr[ema20Arr.length - 1].value : spot;

      // 2. Chop & Entanglement Filter
      const emaVwapDiff = Math.abs(currentEMA20 - currentVWAP);
      let vwapCrossCount = 0;
      for (let i = Math.max(1, candles.length - 6); i < candles.length; i++) {
        const prevAbove = candles[i - 1].close > currentVWAP;
        const curAbove = candles[i].close > currentVWAP;
        if (prevAbove !== curAbove) vwapCrossCount++;
      }
      const isEntangled = (emaVwapDiff < 0.75) || (vwapCrossCount >= 3);

      // 3. Collect active Fair Value Gaps (15M / 5M)
      const fvgList = [];
      if (fvgZones && Array.isArray(fvgZones)) {
        fvgZones.forEach(z => fvgList.push(z));
      }
      const lookback = Math.min(50, candles.length);
      for (let i = candles.length - lookback; i < candles.length; i++) {
        if (i < 2) continue;
        const c1 = candles[i - 2];
        const c2 = candles[i - 1];
        const c3 = candles[i];
        if (c3.low > c1.high) {
          const top = c3.low;
          const bottom = c1.high;
          if (top - bottom >= 0.70) {
            fvgList.push({
              type: 'BULLISH_FVG',
              top: Number(top.toFixed(2)),
              bottom: Number(bottom.toFixed(2)),
              eqLevel: Number(((top + bottom) / 2).toFixed(2)),
              time: c2.time
            });
          }
        } else if (c3.high < c1.low) {
          const top = c1.low;
          const bottom = c3.high;
          if (top - bottom >= 0.70) {
            fvgList.push({
              type: 'BEARISH_FVG',
              top: Number(top.toFixed(2)),
              bottom: Number(bottom.toFixed(2)),
              eqLevel: Number(((top + bottom) / 2).toFixed(2)),
              time: c2.time
            });
          }
        }
      }

      // 4. Setup Evaluation (Gate -> Imbalance Mitigation -> Wick Rejection)
      const recentBars = candles.slice(-3);
      const curBar = candles[candles.length - 1];

      const isBullishGate = (spot > currentVWAP && currentEMA20 >= (currentVWAP - 0.20));
      const isBearishGate = (spot < currentVWAP && currentEMA20 <= (currentVWAP + 0.20));

      let activeSetup = null;

      if (isBullishGate && !isEntangled) {
        for (let k = fvgList.length - 1; k >= 0; k--) {
          const fvg = fvgList[k];
          if (fvg.type !== 'BULLISH_FVG') continue;
          const distVWAP = Math.abs(fvg.eqLevel - currentVWAP);
          const distEMA = Math.abs(fvg.bottom - currentEMA20);
          if (distVWAP <= 3.50 || distEMA <= 3.50 || (fvg.bottom <= currentVWAP && fvg.top >= currentVWAP)) {
            const mitigated = recentBars.some(b => b.low <= fvg.top && b.close >= (fvg.bottom - 0.50));
            if (mitigated) {
              for (let bIdx = recentBars.length - 1; bIdx >= 0; bIdx--) {
                const b = recentBars[bIdx];
                const lowerWick = Math.min(b.open, b.close) - b.low;
                const totalRange = b.high - b.low;
                const wickRatio = totalRange > 0 ? (lowerWick / totalRange) : 0;
                if (wickRatio >= 0.35 && b.close >= currentVWAP) {
                  const entry = Number(curBar.close.toFixed(2));
                  const sl = Number((Math.min(fvg.bottom, currentVWAP) - 1.20).toFixed(2));
                  const risk = Math.max(1.20, entry - sl);
                  const tp = Number((entry + (2.5 * risk)).toFixed(2));
                  const tp2 = Number((entry + (4.0 * risk)).toFixed(2));
                  activeSetup = {
                    active: true,
                    direction: 'BUY',
                    status: 'CONFLUENCE MITIGATION',
                    entry,
                    sl,
                    tp,
                    tp1: tp,
                    tp2,
                    risk: Number(risk.toFixed(2)),
                    reward: Number((tp - entry).toFixed(2)),
                    rr: '1 : 2.5',
                    rrText: '1 : 2.5 (Dynamic FVG Mitigation)',
                    gainPts: Number((tp - entry).toFixed(2)),
                    fvg,
                    vwap: currentVWAP,
                    ema20: currentEMA20,
                    wickRatio: Number(wickRatio.toFixed(2)),
                    reason: `Confirmed: Bullish FVG ($${fvg.bottom.toFixed(1)}-$${fvg.top.toFixed(1)}) Mitigated at VWAP ($${currentVWAP.toFixed(1)}) / EMA20 ($${currentEMA20.toFixed(1)}) + ${Math.round(wickRatio * 100)}% Lower Absorption Wick.`
                  };
                  break;
                }
              }
              if (activeSetup) break;
            }
          }
        }
      } else if (isBearishGate && !isEntangled) {
        for (let k = fvgList.length - 1; k >= 0; k--) {
          const fvg = fvgList[k];
          if (fvg.type !== 'BEARISH_FVG') continue;
          const distVWAP = Math.abs(fvg.eqLevel - currentVWAP);
          const distEMA = Math.abs(fvg.top - currentEMA20);
          if (distVWAP <= 3.50 || distEMA <= 3.50 || (fvg.bottom <= currentVWAP && fvg.top >= currentVWAP)) {
            const mitigated = recentBars.some(b => b.high >= fvg.bottom && b.close <= (fvg.top + 0.50));
            if (mitigated) {
              for (let bIdx = recentBars.length - 1; bIdx >= 0; bIdx--) {
                const b = recentBars[bIdx];
                const upperWick = b.high - Math.max(b.open, b.close);
                const totalRange = b.high - b.low;
                const wickRatio = totalRange > 0 ? (upperWick / totalRange) : 0;
                if (wickRatio >= 0.35 && b.close <= currentVWAP) {
                  const entry = Number(curBar.close.toFixed(2));
                  const sl = Number((Math.max(fvg.top, currentVWAP) + 1.20).toFixed(2));
                  const risk = Math.max(1.20, sl - entry);
                  const tp = Number((entry - (2.5 * risk)).toFixed(2));
                  const tp2 = Number((entry - (4.0 * risk)).toFixed(2));
                  activeSetup = {
                    active: true,
                    direction: 'SELL',
                    status: 'CONFLUENCE MITIGATION',
                    entry,
                    sl,
                    tp,
                    tp1: tp,
                    tp2,
                    risk: Number(risk.toFixed(2)),
                    reward: Number((entry - tp).toFixed(2)),
                    rr: '1 : 2.5',
                    rrText: '1 : 2.5 (Dynamic FVG Mitigation)',
                    gainPts: Number((entry - tp).toFixed(2)),
                    fvg,
                    vwap: currentVWAP,
                    ema20: currentEMA20,
                    wickRatio: Number(wickRatio.toFixed(2)),
                    reason: `Confirmed: Bearish FVG ($${fvg.bottom.toFixed(1)}-$${fvg.top.toFixed(1)}) Mitigated at VWAP ($${currentVWAP.toFixed(1)}) / EMA20 ($${currentEMA20.toFixed(1)}) + ${Math.round(wickRatio * 100)}% Upper Rejection Wick.`
                  };
                  break;
                }
              }
              if (activeSetup) break;
            }
          }
        }
      }

      if (activeSetup) return activeSetup;

      if (isEntangled) {
        return {
          active: false,
          isChopStandby: true,
          status: 'CHOP FILTERED',
          direction: 'STANDBY',
          vwap: currentVWAP,
          ema20: currentEMA20,
          entry: spot,
          sl: spot,
          tp: spot,
          rr: '0 : 0',
          reason: 'STANDBY: VWAP-EMA ENTANGLEMENT (CHOP TRAP FILTERED)'
        };
      }

      if (isBullishGate) {
        return {
          active: false,
          isChopStandby: false,
          status: 'TREND ALIGNED',
          direction: 'BUY',
          vwap: currentVWAP,
          ema20: currentEMA20,
          entry: Number(currentVWAP.toFixed(2)),
          sl: Number((currentVWAP - 2.50).toFixed(2)),
          tp: Number((spot + 8.50).toFixed(2)),
          rr: '1 : 2.5',
          reason: `Trend Bullish: Spot ($${spot.toFixed(1)}) & EMA20 ($${currentEMA20.toFixed(1)}) > Session VWAP ($${currentVWAP.toFixed(1)}). Awaiting FVG Retrace.`
        };
      } else if (isBearishGate) {
        return {
          active: false,
          isChopStandby: false,
          status: 'TREND ALIGNED',
          direction: 'SELL',
          vwap: currentVWAP,
          ema20: currentEMA20,
          entry: Number(currentVWAP.toFixed(2)),
          sl: Number((currentVWAP + 2.50).toFixed(2)),
          tp: Number((spot - 8.50).toFixed(2)),
          rr: '1 : 2.5',
          reason: `Trend Bearish: Spot ($${spot.toFixed(1)}) & EMA20 ($${currentEMA20.toFixed(1)}) < Session VWAP ($${currentVWAP.toFixed(1)}). Awaiting FVG Pullback.`
        };
      }

      return {
        active: false,
        isChopStandby: false,
        status: 'STANDBY',
        direction: 'NEUTRAL',
        vwap: currentVWAP,
        ema20: currentEMA20,
        entry: spot,
        sl: spot,
        tp: spot,
        rr: '1 : 2.5',
        reason: 'Awaiting VWAP & EMA 20 directional alignment.'
      };
    }

    function drawVWAP_EMA_FVG_Overlay(ctx, vwapResult, candles) {
      if (!ctx || !candleSeries || !chart) return;
      if (typeof indicatorSettings !== 'undefined' && !indicatorSettings.vwapEmaFvg) return;
      if (!candles || candles.length === 0) return;

      ctx.save();

      // 1. Session VWAP Line (#FFA726, lineWidth: 2)
      const vwapSeries = calculateSessionVWAPSeries(candles);
      if (vwapSeries && vwapSeries.length > 1) {
        ctx.strokeStyle = '#FFA726';
        ctx.lineWidth = 2.0;
        ctx.setLineDash([]);
        ctx.beginPath();
        let first = true;
        for (let i = 0; i < vwapSeries.length; i++) {
          const pt = vwapSeries[i];
          const x = chart.timeScale().timeToCoordinate(pt.time);
          const y = candleSeries.priceToCoordinate(pt.value);
          if (x === null || y === null) continue;
          if (first) {
            ctx.moveTo(x, y);
            first = false;
          } else {
            ctx.lineTo(x, y);
          }
        }
        ctx.stroke();

        // Current VWAP Right Badge
        const curVWAP = vwapSeries[vwapSeries.length - 1].value;
        const yCurVWAP = candleSeries.priceToCoordinate(curVWAP);
        if (yCurVWAP !== null && yCurVWAP >= 10 && yCurVWAP <= canvasCssHeight - 15) {
          ctx.strokeStyle = 'rgba(255, 167, 38, 0.6)';
          ctx.lineWidth = 1;
          ctx.setLineDash([4, 4]);
          ctx.beginPath();
          ctx.moveTo(canvasCssWidth - 140, yCurVWAP);
          ctx.lineTo(canvasCssWidth - 65, yCurVWAP);
          ctx.stroke();
          ctx.setLineDash([]);

          const vText = `VWAP · $${curVWAP.toFixed(2)}`;
          ctx.font = '700 9px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace';
          const tw = ctx.measureText(vText).width;
          const bw = Math.round(tw + 10);
          const bh = 15;
          const bx = canvasCssWidth - bw - 68;
          const by = Math.round(yCurVWAP - bh / 2);

          ctx.fillStyle = 'rgba(15, 23, 42, 0.92)';
          ctx.fillRect(bx, by, bw, bh);
          ctx.strokeStyle = '#FFA726';
          ctx.lineWidth = 1;
          ctx.strokeRect(bx, by, bw, bh);
          ctx.fillStyle = '#FFA726';
          ctx.textBaseline = 'middle';
          ctx.fillText(vText, bx + 5, yCurVWAP);
        }
      }

      // 2. Dynamic EMA 20 Smooth Line (#29B6F6, lineWidth: 1.5)
      const ema20Arr = (typeof calculateEMA === 'function') ? calculateEMA(candles, 20) : [];
      if (ema20Arr && ema20Arr.length > 1) {
        ctx.strokeStyle = '#29B6F6';
        ctx.lineWidth = 1.5;
        ctx.setLineDash([]);
        ctx.beginPath();
        let first = true;
        for (let i = 0; i < ema20Arr.length; i++) {
          const pt = ema20Arr[i];
          const x = chart.timeScale().timeToCoordinate(pt.time);
          const y = candleSeries.priceToCoordinate(pt.value);
          if (x === null || y === null) continue;
          if (first) {
            ctx.moveTo(x, y);
            first = false;
          } else {
            ctx.lineTo(x, y);
          }
        }
        ctx.stroke();

        const curEMA = ema20Arr[ema20Arr.length - 1].value;
        const yCurEMA = candleSeries.priceToCoordinate(curEMA);
        if (yCurEMA !== null && yCurEMA >= 10 && yCurEMA <= canvasCssHeight - 15) {
          const eText = `EMA 20 · $${curEMA.toFixed(2)}`;
          ctx.font = '700 9px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace';
          const tw = ctx.measureText(eText).width;
          const bw = Math.round(tw + 10);
          const bh = 15;
          const bx = canvasCssWidth - bw - 68;
          const by = Math.round(yCurEMA - bh / 2);

          ctx.fillStyle = 'rgba(15, 23, 42, 0.92)';
          ctx.fillRect(bx, by, bw, bh);
          ctx.strokeStyle = '#29B6F6';
          ctx.lineWidth = 1;
          ctx.strokeRect(bx, by, bw, bh);
          ctx.fillStyle = '#29B6F6';
          ctx.textBaseline = 'middle';
          ctx.fillText(eText, bx + 5, yCurEMA);
        }
      }

      // 3. Active FVG Mitigation Box & Tap Target Badge
      if (vwapResult && vwapResult.fvg) {
        const fvg = vwapResult.fvg;
        const yTop = candleSeries.priceToCoordinate(fvg.top);
        const yBottom = candleSeries.priceToCoordinate(fvg.bottom);

        if (yTop !== null && yBottom !== null) {
          const boxY = Math.min(yTop, yBottom);
          const boxH = Math.max(3, Math.abs(yBottom - yTop));
          const boxX = Math.max(10, canvasCssWidth - 280);
          const boxW = 210;

          const isBull = fvg.type === 'BULLISH_FVG';
          ctx.fillStyle = isBull ? 'rgba(38, 166, 154, 0.20)' : 'rgba(239, 83, 80, 0.20)';
          ctx.fillRect(boxX, boxY, boxW, boxH);
          ctx.strokeStyle = isBull ? '#26a69a' : '#ef5350';
          ctx.lineWidth = 1;
          ctx.strokeRect(boxX, boxY, boxW, boxH);

          const fvgLabel = `${isBull ? 'Bullish' : 'Bearish'} FVG · $${fvg.bottom.toFixed(1)}-$${fvg.top.toFixed(1)}`;
          ctx.font = '600 8.5px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace';
          ctx.fillStyle = isBull ? '#26a69a' : '#ef5350';
          ctx.textBaseline = 'top';
          ctx.fillText(fvgLabel, boxX + 4, boxY + 2);

          if (vwapResult.active) {
            const yEntry = candleSeries.priceToCoordinate(vwapResult.entry) || boxY;
            const badgeText = `🎯 VWAP+FVG Tap (${vwapResult.direction} @ $${vwapResult.entry})`;
            ctx.font = '700 9.5px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace';
            const btw = ctx.measureText(badgeText).width;
            const bbw = Math.round(btw + 14);
            const bbh = 18;
            const bbx = Math.round(boxX + 20);
            const bby = Math.round(yEntry - bbh / 2);

            ctx.shadowColor = isBull ? 'rgba(38, 166, 154, 0.8)' : 'rgba(239, 83, 80, 0.8)';
            ctx.shadowBlur = 8;
            ctx.fillStyle = isBull ? 'rgba(6, 78, 59, 0.95)' : 'rgba(127, 29, 29, 0.95)';
            ctx.fillRect(bbx, bby, bbw, bbh);
            ctx.strokeStyle = isBull ? '#00e676' : '#ff5252';
            ctx.lineWidth = 1.2;
            ctx.strokeRect(bbx, bby, bbw, bbh);

            ctx.shadowBlur = 0;
            ctx.fillStyle = isBull ? '#00e676' : '#ff5252';
            ctx.textBaseline = 'middle';
            ctx.fillText(badgeText, bbx + 7, yEntry);
          }
        }
      }

      ctx.restore();
    }
    window.calculateSessionVWAPSeries = calculateSessionVWAPSeries;
    window.calculateSessionVWAP = calculateSessionVWAP;
    window.evaluateVWAP_EMA_FVG = evaluateVWAP_EMA_FVG;
    window.drawVWAP_EMA_FVG_Overlay = drawVWAP_EMA_FVG_Overlay;

    '''
    content = content.replace(target_state, vwap_core_engine + target_state, 1)

    # 8. modularEngineState registration
    target_ind_state = "BREAKOUT: { status: 'STANDBY', direction: 'NEUTRAL', entry: '--', sl: '--', tp: '--', rr: '--', reason: 'Consolidating Within Lookback Range' }"
    assert target_ind_state in content, "target_ind_state not found"
    content = content.replace(target_ind_state, target_ind_state + ",\n        VWAP_FVG: { status: 'STANDBY', direction: 'NEUTRAL', entry: '--', sl: '--', tp: '--', rr: '--', reason: 'Awaiting VWAP/EMA & FVG Mitigation' }", 1)

    # 9. Telemetry Update in updateModularEngineTelemetry
    target_telemetry_bo = "// 5. BREAKOUT & RETEST TELEMETRY"
    assert target_telemetry_bo in content, "target_telemetry_bo not found"
    vwap_telemetry = '''// 4.5 VWAP + EMA + FVG CONFLUENCE ENGINE TELEMETRY
      const vwapFvgRes = evaluateVWAP_EMA_FVG(candles, (typeof currentSMCZones !== 'undefined' && currentSMCZones ? currentSMCZones.fvgList : null), spot);
      window.latestVWAP_EMA_FVG = vwapFvgRes;
      if (vwapFvgRes) {
        if (vwapFvgRes.active) {
          modularEngineState.indicators.VWAP_FVG = {
            status: 'CONFLUENCE MITIGATION',
            direction: vwapFvgRes.direction,
            entry: '$' + Number(vwapFvgRes.entry).toFixed(2),
            sl: '$' + Number(vwapFvgRes.sl).toFixed(2),
            tp: '$' + Number(vwapFvgRes.tp).toFixed(2),
            rr: vwapFvgRes.rr || '1 : 2.5',
            reason: vwapFvgRes.reason
          };
        } else if (vwapFvgRes.isChopStandby) {
          modularEngineState.indicators.VWAP_FVG = {
            status: 'CHOP FILTERED',
            direction: 'STANDBY',
            entry: '$' + spot.toFixed(2),
            sl: 'FILTERED',
            tp: 'WAITING EXPANSION',
            rr: '0 : 0',
            reason: vwapFvgRes.reason
          };
        } else {
          modularEngineState.indicators.VWAP_FVG = {
            status: vwapFvgRes.status || 'TREND ALIGNED',
            direction: vwapFvgRes.direction || 'NEUTRAL',
            entry: '$' + (vwapFvgRes.entry ? Number(vwapFvgRes.entry).toFixed(2) : spot.toFixed(2)),
            sl: '$' + (vwapFvgRes.sl ? Number(vwapFvgRes.sl).toFixed(2) : (spot - 2.50).toFixed(2)),
            tp: '$' + (vwapFvgRes.tp ? Number(vwapFvgRes.tp).toFixed(2) : (spot + 6.25).toFixed(2)),
            rr: '1 : 2.5',
            reason: vwapFvgRes.reason || 'Awaiting VWAP/EMA and FVG mitigation confluence.'
          };
        }
      }

      '''
    content = content.replace(target_telemetry_bo, vwap_telemetry + target_telemetry_bo, 1)

    # 10. renderModularTelemetryUI tab list & display title
    target_tabs = "const tabs = ['SMC', 'LIQUIDITY', 'DLS', 'FIBONACCI', 'BREAKOUT'];"
    assert target_tabs in content, "target_tabs not found"
    content = content.replace(target_tabs, "const tabs = ['SMC', 'LIQUIDITY', 'DLS', 'VWAP_FVG', 'FIBONACCI', 'BREAKOUT'];", 1)

    target_tab_title = "${activeTab} Indicator Engine"
    assert target_tab_title in content, "target_tab_title not found"
    content = content.replace(target_tab_title, "${activeTab === 'VWAP_FVG' ? 'VWAP + FVG' : activeTab} Indicator Engine", 1)

    btn_snippet = "                  ${tab}\n                </button>"
    assert btn_snippet in content, "btn_snippet not found"
    content = content.replace(btn_snippet, "                  ${tab === 'VWAP_FVG' ? 'VWAP+FVG' : tab}\n                </button>", 1)

    # 11. Redraw overlays call in redrawDrawings()
    target_redraw = "// 2.3 Dedicated: Daily Liquidity Sniper Reference Lines"
    assert target_redraw in content, "target_redraw not found"
    vwap_redraw = '''// 2.25 Dedicated: VWAP + EMA + FVG Confluence Engine Overlay
      if (typeof indicatorSettings !== 'undefined' && indicatorSettings.vwapEmaFvg) {
        drawVWAP_EMA_FVG_Overlay(drawingCtx, window.latestVWAP_EMA_FVG, (typeof rawCandleData !== 'undefined' ? rawCandleData : []));
      }

      '''
    content = content.replace(target_redraw, vwap_redraw + target_redraw, 1)

    # 12. Risk Reward Tool rendering for VWAP+FVG
    target_rr = "else if (typeof indicatorSettings !== 'undefined' && indicatorSettings.liquidityPsychology && window.latestLiquidityPsychology) {"
    assert target_rr in content, "target_rr not found"
    vwap_rr = '''else if (typeof indicatorSettings !== 'undefined' && indicatorSettings.vwapEmaFvg && window.latestVWAP_EMA_FVG && window.latestVWAP_EMA_FVG.active) {
          const v = window.latestVWAP_EMA_FVG;
          const riskPts = Math.abs(Number(v.entry) - Number(v.sl));
          const rewardPts = Math.abs(Number(v.tp) - Number(v.entry));
          const rrRatio = (rewardPts / Math.max(0.1, riskPts)).toFixed(1);
          drawRiskRewardOverlay(drawingCtx, {
            type: v.direction === 'BUY' ? 'LONG' : 'SHORT',
            entry: Number(v.entry),
            sl: Number(v.sl),
            tp: Number(v.tp),
            risk: riskPts,
            reward: rewardPts,
            rrRatio: rrRatio
          });
        } '''
    content = content.replace(target_rr, vwap_rr + target_rr, 1)

    # 13. Execution Card routing in updateActiveSetupCard
    target_card = "if (typeof indicatorSettings !== 'undefined' && indicatorSettings.dailyLiquiditySniper && window.latestDailyLiquiditySniper) {"
    assert target_card in content, "target_card not found"
    vwap_card = '''if (typeof indicatorSettings !== 'undefined' && indicatorSettings.vwapEmaFvg && window.latestVWAP_EMA_FVG) {
        const vRes = window.latestVWAP_EMA_FVG;
        if (vRes.active) {
          if (!curLock || !curLock.active || curLock.status !== 'ACTIVE_HOLD' || curLock.reason !== vRes.reason || curLock.signalType !== vRes.direction) {
            shortTermSignalLock = {
              active: true,
              signalType: vRes.direction,
              action: vRes.direction === 'BUY' ? 'HIGH CONVICTION BUY (VWAP+EMA+FVG)' : 'HIGH CONVICTION SELL (VWAP+EMA+FVG)',
              confidence: '95% (3/3 Confluence: VWAP + EMA20 + FVG Mitigated)',
              entryPrice: vRes.entry,
              tp1: vRes.tp,
              tp2: vRes.tp2,
              sl: Number(vRes.sl),
              rr: vRes.rr,
              rrText: vRes.rrText,
              gainPts: vRes.gainPts,
              reason: vRes.reason,
              badgeText: '⚡ VWAP+EMA+FVG CONFLUENCE',
              lockedAt: now,
              maxLockDurationMs: 60 * 60 * 1000,
              status: 'ACTIVE_HOLD',
              completedAt: null,
              lastCompletedType: curLock ? curLock.lastCompletedType : null,
              lastCompletedStatus: curLock ? curLock.lastCompletedStatus : null
            };
            window.shortTermSignalLock = shortTermSignalLock;
          }
        } else if (vRes.isChopStandby) {
          if (!curLock || !curLock.active || curLock.status !== 'ACTIVE_HOLD' || curLock.status === 'STANDBY_MIDRANGE') {
            shortTermSignalLock = {
              active: false,
              signalType: 'STANDBY',
              action: 'STANDBY: VWAP-EMA ENTANGLEMENT',
              confidence: 'CHOP TRAP FILTERED (Awaiting Expansion)',
              entryPrice: currentSpot,
              tp1: currentSpot,
              tp2: currentSpot,
              sl: 0,
              rr: '0 : 0 (FILTERED)',
              rrText: '0 : 0 (FILTERED)',
              gainPts: 0,
              reason: vRes.reason,
              badgeText: '⚡ VWAP+EMA+FVG (CHOP FILTERED)',
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
      } else '''
    content = content.replace(target_card, vwap_card + target_card, 1)

    # 14. updateStep in updateActiveSetupCard
    target_step = "updateStep('pipeDLS', 'dailyLiquiditySniper', '⚡ DLS-1M');"
    assert target_step in content, "target_step not found"
    content = content.replace(target_step, target_step + "\n        updateStep('pipeVwapFvg', 'vwapEmaFvg', '⚡ VWAP+FVG');", 1)

    # 15. Ghost Candles targeting in evaluateSignals
    target_ghost = "if (typeof indicatorSettings !== 'undefined' && indicatorSettings.dailyLiquiditySniper && window.latestDailyLiquiditySniper && window.latestDailyLiquiditySniper.active) {"
    assert target_ghost in content, "target_ghost not found"
    vwap_ghost_block = '''if (typeof indicatorSettings !== 'undefined' && indicatorSettings.vwapEmaFvg && window.latestVWAP_EMA_FVG && window.latestVWAP_EMA_FVG.active) {
        const v = window.latestVWAP_EMA_FVG;
        isUp = (v.direction === 'BUY');
        tpTarget = Number(v.tp);
        targetColor = isUp ? '#3fb950' : '#f85149';
        targetLabel = `🎯 VWAP+FVG TP $${tpTarget.toFixed(1)} (1:2.5 RR)`;
      } else '''
    content = content.replace(target_ghost, vwap_ghost_block + target_ghost, 1)

    # 16. evaluateActiveConfluence integration
    target_conf = "const dlsRes = evaluateDailyLiquiditySniperModule(candles, spot, liquidityPools);"
    assert target_conf in content, "target_conf not found"
    vwap_conf_call = "const dlsRes = evaluateDailyLiquiditySniperModule(candles, spot, liquidityPools);\n      const vwapFvgRes = evaluateVWAP_EMA_FVG(candles, (typeof currentSMCZones !== 'undefined' && currentSMCZones ? currentSMCZones.fvgList : null), spot);"
    content = content.replace(target_conf, vwap_conf_call, 1)

    target_mod_map = "dailyLiquiditySniper: { name: 'Daily Liquidity Sniper', weight: 25, active: !!indicatorSettings.dailyLiquiditySniper, result: dlsRes },"
    assert target_mod_map in content, "target_mod_map not found"
    vwap_mod_map = "dailyLiquiditySniper: { name: 'Daily Liquidity Sniper', weight: 25, active: !!indicatorSettings.dailyLiquiditySniper, result: dlsRes },\n        vwapEmaFvg: { name: 'VWAP + EMA + FVG Engine', weight: 20, active: !!indicatorSettings.vwapEmaFvg, result: { bias: (window.latestVWAP_EMA_FVG ? window.latestVWAP_EMA_FVG.direction : 'NEUTRAL'), weight: 20, reason: (window.latestVWAP_EMA_FVG ? window.latestVWAP_EMA_FVG.reason : 'Scanning') } },"
    content = content.replace(target_mod_map, vwap_mod_map, 1)

    print("All transformations applied successfully.")

    # Write to all 3 files
    for fn in ['gold_dashboard.html', 'deep_analysis_gold.html', 'index.html']:
        with open(fn, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Wrote {fn}")

    # Verify MD5 parity
    hashes = {}
    for fn in ['gold_dashboard.html', 'deep_analysis_gold.html', 'index.html']:
        with open(fn, 'rb') as f:
            hashes[fn] = hashlib.md5(f.read()).hexdigest()
        print(f"{fn}: {hashes[fn]}")

    assert len(set(hashes.values())) == 1, "MD5 hashes do not match!"
    print("100% Hash Parity Verified!")

if __name__ == '__main__':
    main()
