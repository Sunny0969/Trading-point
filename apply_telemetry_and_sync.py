# apply_telemetry_and_sync.py
import re

with open('gold_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add #modular-indicator-telemetry right beneath Signal History in sidebar
target_sh = """          </div>
        </div>
      </aside>"""

repl_sh = """          </div>
        </div>

        <!-- 4. MODULAR INDICATOR TELEMETRY -->
        <div id="modular-indicator-telemetry" style="margin-top: 10px;"></div>
      </aside>"""

assert target_sh in content, "target_sh not found"
content = content.replace(target_sh, repl_sh, 1)

# 2. Add Breakout toggle in tvIndicatorsMenu
target_menu_dls = """            <!-- Indicator: Daily Liquidity Sniper (1D Sweep + 1M Trigger) -->
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

repl_menu_dls = target_menu_dls + """

            <!-- Indicator: Breakout & Retest (20-Period Dynamic Channel) -->
            <div class="tv-ind-row" onclick="clickModularToggle('breakout', event)">
              <div class="tv-ind-info">
                <div style="display: flex; align-items: center; gap: 6px;">
                  <b style="color: #ff9800;">⚡ Breakout &amp; Retest (20P Dynamic Channel)</b>
                  <span style="font-size: 9px; background: rgba(255,152,0,0.18); color: #ff9800; padding: 1px 4px; border-radius: 4px; font-weight: 700;">WT: 15%</span>
                </div>
                <small>20-Period Dynamic Channel Breakout &amp; Threshold Retest</small>
              </div>
              <label class="toggle-switch" onclick="event.stopPropagation()">
                <input type="checkbox" id="ind-toggle-breakout" checked onchange="toggleModularIndicator('breakout')">
                <span class="toggle-slider"></span>
              </label>
            </div>"""

assert target_menu_dls in content, "target_menu_dls not found"
content = content.replace(target_menu_dls, repl_menu_dls, 1)

# 3. Add Breakout toggle in indicatorsModal
target_modal_dls = """        <div class="indicator-row">
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

repl_modal_dls = target_modal_dls + """

        <div class="indicator-row">
          <div>
            <div style="display: flex; align-items: center; gap: 6px;">
              <b style="color: #ff9800;">⚡ Breakout &amp; Retest (20P Dynamic Channel)</b>
              <span style="font-size: 9px; background: rgba(255,152,0,0.18); color: #ff9800; padding: 1px 4px; border-radius: 4px; font-weight: 700;">WT: 15%</span>
            </div>
            <p style="font-size: 11px; color: #8b949e; margin: 2px 0 0;">20-Period Dynamic Channel Breakout &amp; Threshold Retest</p>
          </div>
          <label class="toggle-switch">
            <input type="checkbox" id="modal-toggle-breakout" checked onchange="toggleModularIndicator('breakout')">
            <span class="toggle-slider"></span>
          </label>
        </div>"""

assert target_modal_dls in content, "target_modal_dls not found"
content = content.replace(target_modal_dls, repl_modal_dls, 1)

# 4. Update DEFAULT_INDICATOR_CONFIG and MODULE_WEIGHTS to include breakout
target_cfg = """    const DEFAULT_INDICATOR_CONFIG = {
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

repl_cfg = """    const DEFAULT_INDICATOR_CONFIG = {
      smcZones: true,        // Module 1: SMC Zones (FVG & Order Blocks) - Weight: 25
      liquidityHunter: true, // Module 2: Liquidity & Order Flow Hunter (Session Sweeps, EQH/EQL) - Weight: 25
      liquidityPsychology: true, // Dedicated: Liquidity & Candle Psychology Engine (Sweep + 5-Candle Confirmation) - Weight: 25
      dailyLiquiditySniper: true, // Dedicated: Daily Liquidity Sniper (1D Sweep + 1M Trigger) - Weight: 25
      autoFib: true,         // Module 3: Auto Fibonacci Golden Pocket (0.50 - 0.618) - Weight: 20
      breakout: true,        // Module: Breakout & Retest (20-Period Dynamic Channel) - Weight: 15
      priceAction: true,     // Module 4: Price Action & Candlestick Scanner - Weight: 15
      momentumSuite: false   // Module 5: Momentum & Trend Suite (EMA 20/50, RSI, MACD) - Weight: 15
    };

    const MODULE_WEIGHTS = {
      smcZones: 25,
      liquidityHunter: 25,
      liquidityPsychology: 25,
      dailyLiquiditySniper: 25,
      autoFib: 20,
      breakout: 15,
      priceAction: 15,
      momentumSuite: 15
    };"""

assert target_cfg in content, "target_cfg not found"
content = content.replace(target_cfg, repl_cfg, 1)

# 5. Add breakoutEnabled variable
target_vars = """    var dailyLiquiditySniperEnabled = !!indicatorSettings.dailyLiquiditySniper;
    window.daily_liquidity_sniper_active = dailyLiquiditySniperEnabled;
    window.latestDailyLiquiditySniper = null;"""

repl_vars = """    var dailyLiquiditySniperEnabled = !!indicatorSettings.dailyLiquiditySniper;
    window.daily_liquidity_sniper_active = dailyLiquiditySniperEnabled;
    window.latestDailyLiquiditySniper = null;
    var breakoutEnabled = !!indicatorSettings.breakout;"""

assert target_vars in content, "target_vars not found"
content = content.replace(target_vars, repl_vars, 1)

# 6. Update labels in toggleModularIndicator
target_labels = """        dailyLiquiditySniper: 'Daily Liquidity Sniper (PDH/PDL 1M Breakout)',
        autoFib: 'Auto Fibonacci Golden Pocket',"""

repl_labels = """        dailyLiquiditySniper: 'Daily Liquidity Sniper (PDH/PDL 1M Breakout)',
        autoFib: 'Auto Fibonacci Golden Pocket',
        breakout: 'Breakout & Retest (20P Dynamic Channel)',"""

assert target_labels in content, "target_labels not found"
content = content.replace(target_labels, repl_labels, 1)

# 7. Update applyModularVisuals and tab sync
target_vis = """      } else if (moduleName === 'dailyLiquiditySniper') {
        dailyLiquiditySniperEnabled = isChecked;
        window.daily_liquidity_sniper_active = isChecked;
      } else if (moduleName === 'autoFib') {"""

repl_vis = """      } else if (moduleName === 'dailyLiquiditySniper') {
        dailyLiquiditySniperEnabled = isChecked;
        window.daily_liquidity_sniper_active = isChecked;
      } else if (moduleName === 'breakout') {
        breakoutEnabled = isChecked;
      } else if (moduleName === 'autoFib') {"""

assert target_vis in content, "target_vis not found"
content = content.replace(target_vis, repl_vis, 1)

# In toggleModularIndicator, auto-switch active telemetry tab when an indicator is toggled
target_toggle_call = """      // Apply specific visual side-effects
      applyModularVisuals(moduleName, newVal);"""

repl_toggle_call = """      // Apply specific visual side-effects
      applyModularVisuals(moduleName, newVal);

      const tabMap = {
        smcZones: 'SMC',
        liquidityHunter: 'LIQUIDITY',
        liquidityPsychology: 'LIQUIDITY',
        dailyLiquiditySniper: 'DLS',
        autoFib: 'FIBONACCI',
        breakout: 'BREAKOUT'
      };
      if (tabMap[moduleName] && typeof modularEngineState !== 'undefined') {
        modularEngineState.activeTab = tabMap[moduleName];
        if (typeof renderModularTelemetryUI === 'function') renderModularTelemetryUI();
      }"""

assert target_toggle_call in content, "target_toggle_call not found"
content = content.replace(target_toggle_call, repl_toggle_call, 1)

# 8. Update detectSmartMoneyZones FVG colors to #00E676 0.15 and #FF5252 0.15 and return Order Blocks
target_fvg_colors = """          color: 'rgba(255, 82, 82, 0.25)', // Soft red/pink #FF5252 with opacity 0.25
          borderColor: 'rgba(255, 82, 82, 0.65)'
        });
      }

      // Primary Key Demand Zone (15M Bullish FVG)
      if (unmitigatedDemand.length > 0) {
        const primary = unmitigatedDemand[0];
        let top = primary.top;
        let bottom = primary.bottom;
        for (const d of unmitigatedDemand.slice(1, 3)) {
          if (Math.abs(d.top - top) <= 4.0 || Math.abs(d.bottom - bottom) <= 4.0) {
            top = Math.max(top, d.top);
            bottom = Math.min(bottom, d.bottom);
          }
        }
        consolidatedZones.push({
          type: 'BULLISH_FVG',
          label: '15m FVG',
          top,
          bottom,
          gap: Number((top - bottom).toFixed(2)),
          eqLevel: Number(((top + bottom) / 2).toFixed(2)),
          time: primary.time,
          hasTapped: Math.abs(currentPrice - top) <= 4.0 || currentPrice <= top,
          color: 'rgba(41, 98, 255, 0.22)',
          borderColor: 'rgba(41, 98, 255, 0.65)'
        });"""

repl_fvg_colors = """          color: 'rgba(255, 82, 82, 0.15)', // Bearish FVG #FF5252 0.15 opacity
          borderColor: 'rgba(255, 82, 82, 0.65)'
        });
      }

      // Primary Key Demand Zone (15M Bullish FVG)
      if (unmitigatedDemand.length > 0) {
        const primary = unmitigatedDemand[0];
        let top = primary.top;
        let bottom = primary.bottom;
        for (const d of unmitigatedDemand.slice(1, 3)) {
          if (Math.abs(d.top - top) <= 4.0 || Math.abs(d.bottom - bottom) <= 4.0) {
            top = Math.max(top, d.top);
            bottom = Math.min(bottom, d.bottom);
          }
        }
        consolidatedZones.push({
          type: 'BULLISH_FVG',
          label: '15m FVG',
          top,
          bottom,
          gap: Number((top - bottom).toFixed(2)),
          eqLevel: Number(((top + bottom) / 2).toFixed(2)),
          time: primary.time,
          hasTapped: Math.abs(currentPrice - top) <= 4.0 || currentPrice <= top,
          color: 'rgba(0, 230, 118, 0.15)', // Bullish FVG #00E676 0.15 opacity
          borderColor: 'rgba(0, 230, 118, 0.65)'
        });"""

assert target_fvg_colors in content, "target_fvg_colors not found"
content = content.replace(target_fvg_colors, repl_fvg_colors, 1)

# Return Order Blocks in detectSmartMoneyZones
target_ob_return = "return { fvgList: consolidatedZones, obList: [], activeRRSetup: activeRR };"
repl_ob_return = """// Format Order Blocks with 50% equilibrium dashed lines
      const formattedOBs = rawOBs.map(ob => ({
        ...ob,
        eqLevel: Number(((ob.top + ob.bottom) / 2).toFixed(2)),
        color: ob.type === 'SUPPLY_OB' ? 'rgba(255, 82, 82, 0.18)' : 'rgba(0, 230, 118, 0.18)',
        borderColor: ob.type === 'SUPPLY_OB' ? 'rgba(255, 82, 82, 0.75)' : 'rgba(0, 230, 118, 0.75)'
      }));

      return { fvgList: consolidatedZones, obList: formattedOBs.slice(-4), activeRRSetup: activeRR };"""

assert target_ob_return in content, "target_ob_return not found"
content = content.replace(target_ob_return, repl_ob_return, 1)

# 9. Update drawSMCZonesOnCanvas to render Order Blocks with distinct boundaries and 50% equilibrium dashed lines
target_ob_stub = """    // Legacy OB stub (merged into primary zones)
    function drawLegacyOBStub(smcData) {"""

repl_ob_stub = """    // Order Block Renderer with distinct boundaries & 50% equilibrium dashed lines
    function drawOrderBlocksOnCanvas(smcData) {
      if (!smcEnabled || !drawingCtx || !drawingCanvas || !candleSeries || !smcData) return;
      const obs = smcData.obList || [];
      if (!Array.isArray(obs) || obs.length === 0) return;

      obs.forEach(ob => {
        const yTop = candleSeries.priceToCoordinate(ob.top);
        const yBottom = candleSeries.priceToCoordinate(ob.bottom);
        if (yTop === null || yBottom === null) return;

        const topY = Math.min(yTop, yBottom);
        const botY = Math.max(yTop, yBottom);
        const height = Math.max(5, botY - topY);
        const startX = 25;
        const width = Math.max(60, canvasCssWidth - startX - 80);

        const isSupply = (ob.type === 'SUPPLY_OB');

        // Box
        drawingCtx.fillStyle = ob.color || (isSupply ? 'rgba(255, 82, 82, 0.15)' : 'rgba(0, 230, 118, 0.15)');
        drawingCtx.fillRect(startX, topY, width, height);

        drawingCtx.strokeStyle = ob.borderColor || (isSupply ? '#ff5252' : '#00e676');
        drawingCtx.lineWidth = 1.2;
        drawingCtx.setLineDash([4, 3]);
        drawingCtx.strokeRect(startX, topY, width, height);
        drawingCtx.setLineDash([]);

        // Label pill
        const obLabel = isSupply ? 'Supply OB' : 'Demand OB';
        drawingCtx.font = '700 9px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace';
        const txtW = drawingCtx.measureText(obLabel).width;
        const pillW = Math.round(txtW + 10);
        const pillH = 15;
        const pillX = startX + 8;
        const pillY = Math.max(2, topY + Math.max(1, (height - pillH) / 2));

        drawingCtx.fillStyle = 'rgba(10, 14, 23, 0.92)';
        drawingCtx.fillRect(pillX, pillY, pillW, pillH);
        drawingCtx.strokeStyle = isSupply ? '#ff5252' : '#00e676';
        drawingCtx.lineWidth = 1;
        drawingCtx.strokeRect(pillX, pillY, pillW, pillH);

        drawingCtx.fillStyle = isSupply ? '#ff5252' : '#00e676';
        drawingCtx.textAlign = 'left';
        drawingCtx.textBaseline = 'middle';
        drawingCtx.fillText(obLabel, pillX + 5, pillY + (pillH / 2));

        // 50% Equilibrium dashed line
        const eq = ob.eqLevel || ((ob.top + ob.bottom) / 2);
        const eqY = candleSeries.priceToCoordinate(eq);
        if (eqY !== null && eqY >= topY - 1 && eqY <= botY + 1) {
          drawingCtx.save();
          drawingCtx.strokeStyle = isSupply ? 'rgba(255, 82, 82, 0.8)' : 'rgba(0, 230, 118, 0.8)';
          drawingCtx.lineWidth = 1;
          drawingCtx.setLineDash([2, 2]);
          drawingCtx.beginPath();
          drawingCtx.moveTo(startX, eqY);
          drawingCtx.lineTo(canvasCssWidth - 85, eqY);
          drawingCtx.stroke();

          drawingCtx.font = '600 8px monospace';
          drawingCtx.fillStyle = isSupply ? '#ff5252' : '#00e676';
          drawingCtx.textAlign = 'right';
          drawingCtx.fillText(`50% EQ $${eq.toFixed(1)}`, canvasCssWidth - 90, eqY - 3);
          drawingCtx.restore();
        }
      });
    }

    // Legacy OB stub (merged into primary zones)
    function drawLegacyOBStub(smcData) {"""

assert target_ob_stub in content, "target_ob_stub not found"
content = content.replace(target_ob_stub, repl_ob_stub, 1)

# In redrawDrawings, call drawOrderBlocksOnCanvas
target_redraw_smc = """      // 1. Smart Money Concept (SMC) Key Supply & Demand Zones
      if (currentSMCZones && smcEnabled) {
        drawSMCZonesOnCanvas(currentSMCZones);
      }"""

repl_redraw_smc = """      // 1. Smart Money Concept (SMC) Key Supply & Demand Zones (FVG & Order Blocks)
      if (currentSMCZones && smcEnabled) {
        drawSMCZonesOnCanvas(currentSMCZones);
        drawOrderBlocksOnCanvas(currentSMCZones);
      }"""

assert target_redraw_smc in content, "target_redraw_smc not found"
content = content.replace(target_redraw_smc, repl_redraw_smc, 1)

# 10. Update Breakout Overlay call in redrawDrawings
target_redraw_bo = """      // 1.5 Draw Quantitative Breakout Line (Only when SMC and Liquidity Psychology are off to avoid collision)
      if (!smcEnabled && (!indicatorSettings || !indicatorSettings.liquidityPsychology)) {
        try { drawBreakoutOverlayOnCanvas(drawingCtx); } catch (boDrawErr) {}
      }"""

repl_redraw_bo = """      // 1.5 Draw Quantitative Breakout & Retest Channel Threshold
      if (typeof indicatorSettings !== 'undefined' && indicatorSettings.breakout) {
        try { drawBreakoutOverlayOnCanvas(drawingCtx); } catch (boDrawErr) {}
      } else if (!smcEnabled && (!indicatorSettings || !indicatorSettings.liquidityPsychology)) {
        try { drawBreakoutOverlayOnCanvas(drawingCtx); } catch (boDrawErr) {}
      }"""

assert target_redraw_bo in content, "target_redraw_bo not found"
content = content.replace(target_redraw_bo, repl_redraw_bo, 1)

# 11. Fix Ghost Candle Projection on SL / Invalidation
target_ghost_sl = """      // 1. If Setup was Stopped Out / Invalidated, Ghost Candle MUST immediately track downside to next demand
      if (typeof shortTermSignalLock !== 'undefined' && shortTermSignalLock.status === 'SL_HIT') {
        isUp = false;
        const nextSupportTarget = (typeof supportLevel === 'number' && supportLevel < currentPrice) ? supportLevel : (currentPrice - (atr * 2.5));"""

repl_ghost_sl = """      // 1. If Setup was Stopped Out / Invalidated, Ghost Candle MUST immediately track downside/upside expansion
      if (typeof shortTermSignalLock !== 'undefined' && shortTermSignalLock.status === 'SL_HIT') {
        const wasBuy = (shortTermSignalLock.lastCompletedType === 'BUY' || shortTermSignalLock.signalType === 'BUY');
        isUp = !wasBuy; // If Long stopped out -> downside expansion. If Short stopped out -> upside expansion.
        const nextTarget = isUp 
          ? ((typeof resistanceLevel === 'number' && resistanceLevel > currentPrice) ? resistanceLevel : (currentPrice + (atr * 2.5)))
          : ((typeof supportLevel === 'number' && supportLevel < currentPrice) ? supportLevel : (currentPrice - (atr * 2.5)));
        targetLabel = isUp ? `🎯 Invalidation Expansion $${nextTarget.toFixed(1)} (Upside)` : `🎯 Next Demand $${nextTarget.toFixed(1)} (Downside Extension)`;
        targetColor = isUp ? '#2ea043' : '#f85149';

        if (isUp) {
          c1_open = currentPrice; c1_close = c1_open + (atr * 0.70); c1_high = c1_close + (atr * 0.35); c1_low = c1_open - (atr * 0.15);
          c2_open = c1_close; c2_close = c2_open + (atr * 0.85); c2_high = c2_close + (atr * 0.40); c2_low = c2_open - (atr * 0.15);
          c3_open = c2_close; c3_close = Math.max(nextTarget, c3_open + (atr * 0.95)); c3_high = c3_close + (atr * 0.45); c3_low = c3_open - (atr * 0.20);
        } else {
          c1_open = currentPrice; c1_close = c1_open - (atr * 0.70); c1_low = c1_close - (atr * 0.35); c1_high = c1_open + (atr * 0.15);
          c2_open = c1_close; c2_close = c2_open - (atr * 0.85); c2_low = c2_close - (atr * 0.40); c2_high = c2_open + (atr * 0.15);
          c3_open = c2_close; c3_close = Math.min(nextTarget, c3_open - (atr * 0.95)); c3_low = c3_close - (atr * 0.45); c3_high = c3_open + (atr * 0.20);
        }
      } else if (typeof shortTermSignalLock !== 'undefined' && shortTermSignalLock.status === 'STANDBY_MIDRANGE') {
        isUp = currentPrice >= (window.currentEMA20 || currentPrice);
        targetLabel = `Standby Pivot $${currentPrice.toFixed(1)}`;
        targetColor = '#eab308';
        c1_open = currentPrice; c1_close = c1_open + (isUp ? 0.4 : -0.4); c1_high = currentPrice + 0.8; c1_low = currentPrice - 0.8;
        c2_open = c1_close; c2_close = c2_open + (isUp ? 0.3 : -0.3); c2_high = c2_open + 0.7; c2_low = c2_open - 0.7;
        c3_open = c2_close; c3_close = c3_open + (isUp ? 0.2 : -0.2); c3_high = c3_open + 0.6; c3_low = c3_open - 0.6;"""

assert target_ghost_sl in content, "target_ghost_sl not found"
content = content.replace(target_ghost_sl, repl_ghost_sl, 1)

# 12. Add modularEngineState and renderModularTelemetryUI implementation
telemetry_engine_code = '''
    // ==========================================
    // DEDICATED PER-INDICATOR SIGNAL TELEMETRY ENGINE
    // Single Source of Truth Telemetry for: SMC, LIQUIDITY, DLS, FIBONACCI, BREAKOUT
    // ==========================================
    const modularEngineState = {
      activeTab: 'SMC',
      indicators: {
        SMC: { status: 'STANDBY', direction: 'NEUTRAL', entry: '--', sl: '--', tp: '--', rr: '--', reason: 'Awaiting Zone Mitigation' },
        LIQUIDITY: { status: 'STANDBY', direction: 'NEUTRAL', entry: '--', sl: '--', tp: '--', rr: '--', reason: 'Scanning Session Ranges' },
        DLS: { status: 'STANDBY', direction: 'NEUTRAL', entry: '--', sl: '--', tp: '--', rr: '--', reason: 'Price Inside Daily Range' },
        FIBONACCI: { status: 'STANDBY', direction: 'NEUTRAL', entry: '--', sl: '--', tp: '--', rr: '--', reason: 'Awaiting 0.618 Golden Retracement' },
        BREAKOUT: { status: 'STANDBY', direction: 'NEUTRAL', entry: '--', sl: '--', tp: '--', rr: '--', reason: 'Consolidating Within Lookback Range' }
      }
    };

    function updateModularEngineTelemetry(candles, currentSpot) {
      if (!candles || candles.length < 5) return;
      const spot = (typeof currentSpot === 'number' && currentSpot > 0) ? currentSpot : candles[candles.length - 1].close;

      // 1. SMC TELEMETRY
      const smc = (typeof currentSMCZones !== 'undefined' && currentSMCZones && currentSMCZones.fvgList)
        ? currentSMCZones
        : (typeof detectSmartMoneyZones === 'function' ? detectSmartMoneyZones(candles) : null);

      if (smc && smc.activeRRSetup) {
        const isShort = (smc.activeRRSetup.type === 'SHORT' || smc.activeRRSetup.type === 'SELL');
        modularEngineState.indicators.SMC = {
          status: 'TRIGGERED',
          direction: isShort ? 'SELL' : 'BUY',
          entry: '$' + Number(smc.activeRRSetup.entry).toFixed(2),
          sl: '$' + Number(smc.activeRRSetup.sl).toFixed(2),
          tp: '$' + Number(smc.activeRRSetup.tp).toFixed(2),
          rr: '1 : ' + (smc.activeRRSetup.rrRatio || '3.5'),
          reason: isShort
            ? 'Bearish 15M FVG Mitigated + EMA 20 Rejection confirmed.'
            : 'Bullish 15M FVG Mitigated + EMA 20 Bounce confirmed.'
        };
      } else if (smc && smc.fvgList && smc.fvgList.length > 0) {
        const supply = smc.fvgList.find(z => z.type === 'BEARISH_FVG');
        const demand = smc.fvgList.find(z => z.type === 'BULLISH_FVG');
        const targetZone = supply || demand;
        const isSupply = (targetZone && targetZone.type === 'BEARISH_FVG');
        modularEngineState.indicators.SMC = {
          status: 'SCANNING',
          direction: 'NEUTRAL',
          entry: targetZone ? '$' + (isSupply ? targetZone.bottom : targetZone.top).toFixed(2) : '--',
          sl: targetZone ? '$' + (isSupply ? targetZone.top + 2.0 : targetZone.bottom - 2.0).toFixed(2) : '--',
          tp: targetZone ? '$' + (isSupply ? targetZone.bottom - 16.0 : targetZone.top + 16.0).toFixed(2) : '--',
          rr: '1 : 3.5',
          reason: 'Awaiting 15M FVG / Order Block zone mitigation.'
        };
      } else {
        modularEngineState.indicators.SMC = {
          status: 'STANDBY',
          direction: 'NEUTRAL',
          entry: '--',
          sl: '--',
          tp: '--',
          rr: '--',
          reason: 'Awaiting 15M FVG / Order Block zone formation.'
        };
      }

      // 2. LIQUIDITY & CANDLE PSYCHOLOGY TELEMETRY
      if (window.latestLiquidityPsychology) {
        const psy = window.latestLiquidityPsychology;
        modularEngineState.indicators.LIQUIDITY = {
          status: 'TRIGGERED',
          direction: psy.type === 'BUY' ? 'BUY' : 'SELL',
          entry: '$' + Number(psy.entry).toFixed(2),
          sl: '$' + Number(psy.sl).toFixed(2),
          tp: '$' + Number(psy.tp).toFixed(2),
          rr: psy.rr || '1 : 3.5',
          reason: psy.reason || 'Confirmed: Liquidity Swept + 5-Bar Psychological Absorption Verified.'
        };
      } else if (window.latestLiquiditySweep) {
        const sw = window.latestLiquiditySweep;
        modularEngineState.indicators.LIQUIDITY = {
          status: 'TRIGGERED',
          direction: sw.type,
          entry: '$' + Number(sw.entry).toFixed(2),
          sl: '$' + Number(sw.sl).toFixed(2),
          tp: '$' + Number(sw.tp).toFixed(2),
          rr: sw.rr || '1 : 3.0',
          reason: sw.reason || 'Institutional Liquidity Raid Swept + Reversal.'
        };
      } else {
        modularEngineState.indicators.LIQUIDITY = {
          status: 'SCANNING',
          direction: 'NEUTRAL',
          entry: '--',
          sl: '--',
          tp: '--',
          rr: '--',
          reason: 'Scanning Asian/London Session and EQH/EQL Liquidity Pools.'
        };
      }

      // 3. DAILY LIQUIDITY SNIPER (DLS-1M) TELEMETRY
      if (window.latestDailyLiquiditySniper) {
        const dls = window.latestDailyLiquiditySniper;
        if (dls.active) {
          modularEngineState.indicators.DLS = {
            status: 'TRIGGERED',
            direction: dls.direction,
            entry: '$' + Number(dls.entry).toFixed(2),
            sl: '$' + Number(dls.sl).toFixed(2),
            tp: '$' + Number(dls.tp1).toFixed(2),
            rr: dls.rrText || '1 : 4.0',
            reason: dls.reason
          };
        } else if (dls.isStandby) {
          modularEngineState.indicators.DLS = {
            status: 'STANDBY',
            direction: 'STANDBY',
            entry: '$' + spot.toFixed(2),
            sl: 'NO TRADE ZONE',
            tp: 'WAITING BOUNDARY',
            rr: '0 : 0',
            reason: 'Price Inside Daily Range between PDH and PDL (No-Trade Zone).'
          };
        } else {
          modularEngineState.indicators.DLS = {
            status: 'SCANNING',
            direction: 'NEUTRAL',
            entry: '--',
            sl: '--',
            tp: '--',
            rr: '--',
            reason: 'Scanning PDH/PDL 1M Breakout Triggers.'
          };
        }
      } else {
        modularEngineState.indicators.DLS = {
          status: 'SCANNING',
          direction: 'NEUTRAL',
          entry: '--',
          sl: '--',
          tp: '--',
          rr: '--',
          reason: 'Scanning PDH/PDL 1M Breakout Triggers.'
        };
      }

      // 4. AUTO FIBONACCI GOLDEN POCKET TELEMETRY
      const slice50 = candles.slice(-50);
      if (slice50.length >= 10) {
        const swingH = Math.max(...slice50.map(c => c.high));
        const swingL = Math.min(...slice50.map(c => c.low));
        const fibRange = Math.max(0.5, swingH - swingL);
        const p50 = Number((swingL + (fibRange * 0.50)).toFixed(2));
        const p618 = Number((swingL + (fibRange * 0.618)).toFixed(2));
        const p786 = Number((swingL + (fibRange * 0.786)).toFixed(2));

        const inPocket = (spot >= Math.min(p50, p618) && spot <= Math.max(p50, p618));
        const nearPocket = (Math.abs(spot - p618) <= 2.5);

        if (inPocket || nearPocket) {
          const isUpBounce = spot >= p618;
          const risk = Math.max(1.5, Math.abs(spot - (isUpBounce ? swingL : swingH)));
          const reward = Math.max(3.0, Math.abs((isUpBounce ? swingH : swingL) - spot));
          modularEngineState.indicators.FIBONACCI = {
            status: 'TRIGGERED',
            direction: isUpBounce ? 'BUY' : 'SELL',
            entry: '$' + spot.toFixed(2),
            sl: '$' + (isUpBounce ? (swingL - 1.5).toFixed(2) : (swingH + 1.5).toFixed(2)),
            tp: '$' + (isUpBounce ? swingH.toFixed(2) : swingL.toFixed(2)),
            rr: '1 : ' + (reward / risk).toFixed(1),
            reason: `Price interacting with 0.50 - 0.618 Golden Pocket ($${p50.toFixed(1)} - $${p618.toFixed(1)}).`
          };
        } else {
          modularEngineState.indicators.FIBONACCI = {
            status: 'STANDBY',
            direction: 'NEUTRAL',
            entry: '$' + p618.toFixed(2),
            sl: '$' + (swingL - 1.5).toFixed(2),
            tp: '$' + swingH.toFixed(2),
            rr: '1 : 2.5',
            reason: `Awaiting 0.618 Golden Pocket Retracement ($${p618.toFixed(1)}). Range: $${swingL.toFixed(1)} - $${swingH.toFixed(1)}.`
          };
        }
      }

      // 5. BREAKOUT & RETEST TELEMETRY
      if (window.activeBreakoutSetup && (window.activeBreakoutSetup.status === 'CONFIRMED_RETEST' || window.activeBreakoutSetup.status === 'RETESTING')) {
        const bo = window.activeBreakoutSetup;
        const isBull = bo.type === 'BULLISH_BREAKOUT_RETEST';
        modularEngineState.indicators.BREAKOUT = {
          status: bo.status === 'CONFIRMED_RETEST' ? 'TRIGGERED' : 'SCANNING',
          direction: isBull ? 'BUY' : 'SELL',
          entry: '$' + Number(bo.entryPrice).toFixed(2),
          sl: '$' + Number(bo.invalidationLevel).toFixed(2),
          tp: '$' + Number(bo.targetLevel).toFixed(2),
          rr: bo.rrText || '1 : 3.0',
          reason: bo.reason || '20-Period Dynamic Channel Breakout & Confirmed Retest.'
        };
      } else {
        const slice20 = candles.slice(-20);
        const chanHigh = Math.max(...slice20.map(c => c.high));
        const chanLow = Math.min(...slice20.map(c => c.low));
        const chanMid = (chanHigh + chanLow) / 2;
        const isUpper = spot >= chanMid;
        modularEngineState.indicators.BREAKOUT = {
          status: 'STANDBY',
          direction: 'NEUTRAL',
          entry: '$' + (isUpper ? chanHigh.toFixed(2) : chanLow.toFixed(2)),
          sl: '$' + chanMid.toFixed(2),
          tp: '$' + (isUpper ? (chanHigh + (chanHigh - chanLow)).toFixed(2) : (chanLow - (chanHigh - chanLow)).toFixed(2)),
          rr: '1 : 2.0',
          reason: `Consolidating within 20-period lookback channel ($${chanLow.toFixed(1)} - $${chanHigh.toFixed(1)}).`
        };
      }

      // Re-render telemetry UI
      renderModularTelemetryUI();
    }

    function renderModularTelemetryUI() {
      const container = document.getElementById('modular-indicator-telemetry');
      if (!container) return;

      const activeTab = modularEngineState.activeTab || 'SMC';
      const activeData = (modularEngineState.indicators && modularEngineState.indicators[activeTab])
        ? modularEngineState.indicators[activeTab]
        : { status: 'STANDBY', direction: 'NEUTRAL', entry: '--', sl: '--', tp: '--', rr: '--', reason: 'Awaiting telemetry' };

      const isBuy = activeData.direction === 'BUY';
      const isSell = activeData.direction === 'SELL';
      const isStandby = (activeData.direction === 'STANDBY' || activeData.direction === 'NEUTRAL');

      let badgeBg = 'rgba(139, 148, 158, 0.15)';
      let badgeColor = '#8b949e';
      let badgeBorder = 'rgba(139, 148, 158, 0.35)';

      if (isBuy) {
        badgeBg = 'rgba(46, 160, 67, 0.18)';
        badgeColor = '#3fb950';
        badgeBorder = 'rgba(46, 160, 67, 0.45)';
      } else if (isSell) {
        badgeBg = 'rgba(248, 81, 73, 0.18)';
        badgeColor = '#f85149';
        badgeBorder = 'rgba(248, 81, 73, 0.45)';
      } else if (activeData.direction === 'STANDBY') {
        badgeBg = 'rgba(234, 179, 8, 0.15)';
        badgeColor = '#eab308';
        badgeBorder = 'rgba(234, 179, 8, 0.4)';
      }

      const tabs = ['SMC', 'LIQUIDITY', 'DLS', 'FIBONACCI', 'BREAKOUT'];

      container.innerHTML = `
        <div class="terminal-card clean-signal-card" style="padding: 12px; margin-top: 10px; border-radius: 12px; background: rgba(18, 20, 26, 0.95); border: 1px solid rgba(255, 255, 255, 0.08); box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);">
          <!-- Header -->
          <div style="display: flex; align-items: center; justify-content: space-between; padding-bottom: 8px; border-bottom: 1px solid rgba(255, 255, 255, 0.08);">
            <span style="font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: #ffd700; display: flex; align-items: center; gap: 6px;">
              <span style="display: inline-block; width: 7px; height: 7px; border-radius: 50%; background: #ffd700; box-shadow: 0 0 8px #ffd700;"></span>
              ${activeTab} Indicator Engine
            </span>
            <span style="font-size: 10px; padding: 2px 7px; border-radius: 10px; background: ${badgeBg}; color: ${badgeColor}; border: 1px solid ${badgeBorder}; font-family: monospace; font-weight: 700;">
              ${activeData.direction}
            </span>
          </div>

          <!-- Tab Switcher -->
          <div style="display: flex; gap: 4px; margin: 8px 0; overflow-x: auto; padding-bottom: 2px;">
            ${tabs.map(tab => {
              const isActive = (modularEngineState.activeTab === tab);
              const activeStyle = isActive
                ? 'background: #ffd700; color: #000; font-weight: 800; border: 1px solid #ffd700; box-shadow: 0 0 10px rgba(255, 215, 0, 0.25);'
                : 'background: rgba(255, 255, 255, 0.05); color: #8b949e; border: 1px solid rgba(255, 255, 255, 0.08);';
              return `
                <button type="button" onclick="switchModularTab('${tab}')"
                        style="flex: 1; min-width: 50px; font-size: 9.5px; padding: 4px 6px; border-radius: 6px; cursor: pointer; transition: all 0.15s ease; ${activeStyle}">
                  ${tab}
                </button>
              `;
            }).join('')}
          </div>

          <!-- Coordinates Grid -->
          <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; margin: 8px 0; text-align: center; font-family: monospace;">
            <div style="padding: 7px 4px; border-radius: 8px; background: rgba(0, 0, 0, 0.35); border: 1px solid rgba(255, 255, 255, 0.06);">
              <div style="font-size: 8.5px; color: #8b949e; font-family: -apple-system, BlinkMacSystemFont, sans-serif;">ENTRY</div>
              <div style="font-size: 11px; font-weight: 700; color: #f0f6fc; margin-top: 2px;">${activeData.entry}</div>
            </div>
            <div style="padding: 7px 4px; border-radius: 8px; background: rgba(0, 0, 0, 0.35); border: 1px solid rgba(255, 255, 255, 0.06);">
              <div style="font-size: 8.5px; color: rgba(248, 81, 73, 0.85); font-family: -apple-system, BlinkMacSystemFont, sans-serif;">STOP LOSS</div>
              <div style="font-size: 11px; font-weight: 700; color: #f85149; margin-top: 2px;">${activeData.sl}</div>
            </div>
            <div style="padding: 7px 4px; border-radius: 8px; background: rgba(0, 0, 0, 0.35); border: 1px solid rgba(255, 255, 255, 0.06);">
              <div style="font-size: 8.5px; color: rgba(63, 185, 80, 0.85); font-family: -apple-system, BlinkMacSystemFont, sans-serif;">TARGET (TP)</div>
              <div style="font-size: 11px; font-weight: 700; color: #3fb950; margin-top: 2px;">${activeData.tp}</div>
            </div>
          </div>

          <!-- Status & RR -->
          <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 4px; padding-top: 6px; border-top: 1px solid rgba(255, 255, 255, 0.06); font-size: 10px; color: #8b949e;">
            <span style="color: #ffd700; font-weight: 600;">Status: <span style="color: #f0f6fc;">${activeData.status}</span></span>
            <span style="font-family: monospace; font-weight: 700; color: #3fb950;">RR: ${activeData.rr}</span>
          </div>

          <!-- Reasoning Footnote -->
          <div style="margin-top: 5px; font-size: 10.5px; color: #8b949e; display: flex; align-items: flex-start; gap: 4px; line-height: 1.35;">
            <span style="color: #ffd700; font-weight: 700;">↳</span>
            <span>${activeData.reason}</span>
          </div>
        </div>
      `;
    }

    function switchModularTab(tab) {
      if (typeof modularEngineState !== 'undefined') {
        modularEngineState.activeTab = tab;
        renderModularTelemetryUI();
      }
    }
    window.switchModularTab = switchModularTab;
    window.modularEngineState = modularEngineState;
    window.renderModularTelemetryUI = renderModularTelemetryUI;
    window.updateModularEngineTelemetry = updateModularEngineTelemetry;
'''

target_anchor_engine = "    window.drawDailyLiquiditySniperOverlay = drawDailyLiquiditySniperOverlay;"
repl_anchor_engine = target_anchor_engine + "\n" + telemetry_engine_code

assert target_anchor_engine in content, "target_anchor_engine not found"
content = content.replace(target_anchor_engine, repl_anchor_engine, 1)

# 13. Call updateModularEngineTelemetry inside evaluateSignals
target_eval_sig_call = """      updateActiveSetupCard(confluence, currentCandle, dynLow, dynHigh);
      return confluence;"""

repl_eval_sig_call = """      updateActiveSetupCard(confluence, currentCandle, dynLow, dynHigh);
      if (typeof updateModularEngineTelemetry === 'function') {
        updateModularEngineTelemetry(candleData, currentPrice);
      }
      return confluence;"""

assert target_eval_sig_call in content, "target_eval_sig_call not found"
content = content.replace(target_eval_sig_call, repl_eval_sig_call, 1)

# 14. Write back to gold_dashboard.html, deep_analysis_gold.html, index.html
with open('gold_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)

with open('deep_analysis_gold.html', 'w', encoding='utf-8') as f:
    f.write(content)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Successfully applied real-time sync, on-chart overlays, and dynamic modular telemetry across all 3 files!')
