import sys

def main():
    with open('gold_dashboard.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Dropdown menu: add SMC Inducement & CHoCH Supply Sniper toggle
    dropdown_needle = "<!-- Indicator 1: Smart Money Structure (15M FVG & Order Blocks) -->"
    dropdown_sniper = '''<!-- Indicator: SMC Inducement & CHoCH Supply Sniper -->
            <div class="tv-ind-row" onclick="clickModularToggle('smcInducementSupply', event)">
              <div class="tv-ind-info">
                <div style="display: flex; align-items: center; gap: 6px;">
                  <b style="color: #e879f9;">⚡ SMC Inducement &amp; CHoCH Supply Sniper</b>
                  <span style="font-size: 9px; background: rgba(232,121,249,0.18); color: #e879f9; padding: 1px 4px; border-radius: 4px; font-weight: 700;">WT: 25%</span>
                </div>
                <small>CHoCH + EQL Liquidity + Inducement (X) Purge &amp; Extreme Supply Tap</small>
              </div>
              <label class="toggle-switch" onclick="event.stopPropagation()">
                <input type="checkbox" id="ind-toggle-smcInducementSupply" checked onchange="toggleModularIndicator('smcInducementSupply')">
                <span class="toggle-slider"></span>
              </label>
            </div>

            '''
    if dropdown_needle not in html:
        print("ERROR: dropdown_needle not found!")
        return False
    html = html.replace(dropdown_needle, dropdown_sniper + dropdown_needle, 1)

    # 2. Modal indicator list: add SMC Inducement & CHoCH Supply Sniper
    modal_needle = '<div class="indicator-row">\n          <div>\n            <div style="display: flex; align-items: center; gap: 6px;">\n              <b style="color: #58a6ff;">🏛️ SMC Zones (15m FVG &amp; OB)</b>'
    alt_modal = '<div class="indicator-row">\r\n          <div>\r\n            <div style="display: flex; align-items: center; gap: 6px;">\r\n              <b style="color: #58a6ff;">🏛️ SMC Zones (15m FVG &amp; OB)</b>'
    modal_sniper = '''<div class="indicator-row" onclick="clickModularToggle('smcInducementSupply', event)">
          <div>
            <div style="display: flex; align-items: center; gap: 6px;">
              <b style="color: #e879f9;">⚡ SMC Inducement &amp; CHoCH Supply Sniper</b>
              <span style="font-size: 9px; background: rgba(232,121,249,0.18); color: #e879f9; padding: 1px 4px; border-radius: 4px; font-weight: 700;">WT: 25%</span>
            </div>
            <p style="font-size: 11px; color: #8b949e; margin: 2px 0 0;">CHoCH + EQL Liquidity + Inducement (X) Purge &amp; Extreme Supply Tap</p>
          </div>
          <label class="toggle-switch" onclick="event.stopPropagation()">
            <input type="checkbox" id="modal-toggle-smcInducementSupply" checked onchange="toggleModularIndicator('smcInducementSupply')">
            <span class="toggle-slider"></span>
          </label>
        </div>

        '''
    if modal_needle in html:
        html = html.replace(modal_needle, modal_sniper + modal_needle, 1)
    elif alt_modal in html:
        html = html.replace(alt_modal, modal_sniper + alt_modal, 1)
    else:
        print("ERROR: modal indicator row not found!")
        return False

    # 3. DEFAULT_INDICATOR_CONFIG and MODULE_WEIGHTS
    cfg_needle = 'smcZones: true,        // Module 1: SMC Zones (FVG & Order Blocks) - Weight: 25'
    cfg_sniper = '''smcZones: true,        // Module 1: SMC Zones (FVG & Order Blocks) - Weight: 25
      smcInducementSupply: (function() {
        try {
          const v = localStorage.getItem('indicator_smc_inducement_active');
          return v !== null ? (v === 'true') : true;
        } catch (e) { return true; }
      })(), // Dedicated: SMC Inducement & CHoCH Supply Sniper - Weight: 25'''
    if cfg_needle not in html:
        print("ERROR: cfg_needle not found!")
        return False
    html = html.replace(cfg_needle, cfg_sniper, 1)

    weights_needle = 'smcZones: 25,'
    weights_sniper = '''smcZones: 25,
      smcInducementSupply: 25,'''
    if weights_needle not in html:
        print("ERROR: weights_needle not found!")
        return False
    html = html.replace(weights_needle, weights_sniper, 1)

    # 4. State variable initialization
    state_needle = 'var smcPullbackSniperEnabled = (() => {'
    state_sniper = '''var smcInducementSupplyEnabled = (() => {
      try {
        const v = localStorage.getItem('indicator_smc_inducement_active');
        return v !== null ? (v === 'true') : true;
      } catch (e) { return true; }
    })();
    window.smcInducementSupplyEnabled = smcInducementSupplyEnabled;
    window.latestSMC_InducementSupply = null;
    var smcPullbackSniperEnabled = (() => {'''
    if state_needle not in html:
        print("ERROR: state_needle not found!")
        return False
    html = html.replace(state_needle, state_sniper, 1)

    # 5. toggleModularIndicator & applyModularVisuals
    toggle_needle = "if (moduleName === 'smcPullbackSniper') {"
    toggle_sniper = '''if (moduleName === 'smcInducementSupply') {
        try {
          localStorage.setItem('indicator_smc_inducement_active', newVal ? 'true' : 'false');
          window.smcInducementSupplyEnabled = newVal;
        } catch (e) {}
      } else if (moduleName === 'smcPullbackSniper') {'''
    if toggle_needle not in html:
        print("ERROR: toggle_needle not found!")
        return False
    html = html.replace(toggle_needle, toggle_sniper, 1)

    # In tabMap:
    tabmap_needle = "smcPullbackSniper: 'OB_FIBO',"
    tabmap_sniper = "smcPullbackSniper: 'OB_FIBO',\n        smcInducementSupply: 'CHOCH_SUPPLY',"
    if tabmap_needle not in html:
        print("ERROR: tabmap_needle not found!")
        return False
    html = html.replace(tabmap_needle, tabmap_sniper, 1)

    # In labels:
    labels_needle = "smcPullbackSniper: 'SMC M5 Pullback Sniper (BOS + OB + 0.618 Fibo)',"
    labels_sniper = "smcPullbackSniper: 'SMC M5 Pullback Sniper (BOS + OB + 0.618 Fibo)',\n        smcInducementSupply: 'SMC Inducement & CHoCH Supply Sniper',"
    if labels_needle not in html:
        print("ERROR: labels_needle not found!")
        return False
    html = html.replace(labels_needle, labels_sniper, 1)

    # In applyModularVisuals:
    apply_needle = "if (moduleName === 'smcPullbackSniper') {"
    apply_sniper = '''if (moduleName === 'smcInducementSupply') {
        smcInducementSupplyEnabled = isChecked;
        window.smcInducementSupplyEnabled = isChecked;
        try {
          localStorage.setItem('indicator_smc_inducement_active', isChecked ? 'true' : 'false');
        } catch (e) {}
      } else if (moduleName === 'smcPullbackSniper') {'''
    if apply_needle not in html:
        print("ERROR: apply_needle not found!")
        return False
    html = html.replace(apply_needle, apply_sniper, 1)

    # 6. Evaluation and Canvas Drawing Functions:
    # Insert evaluateSMC_InducementSupply and drawSMC_InducementSupplyOverlay before updateModularEngineTelemetry
    engine_needle = 'function updateModularEngineTelemetry(candles, currentSpot) {'
    engine_code = '''// ==========================================
    // SMC INDUCEMENT & CHOCH SUPPLY SNIPER ENGINE
    // ==========================================
    function evaluateSMC_InducementSupply(candles) {
      if (!candles || candles.length < 25) return null;

      const currentBar = candles[candles.length - 1];

      // 1. Identify Extreme Supply Zone (Highest swing high in recent 30 bars)
      let supplyHigh = -Infinity;
      let supplyLow = -Infinity;
      let supplyIdx = -1;

      const lookbackStart = Math.max(0, candles.length - 30);
      const lookbackEnd = Math.max(lookbackStart + 1, candles.length - 6);

      for (let i = lookbackStart; i < lookbackEnd; i++) {
        if (candles[i].high > supplyHigh) {
          supplyHigh = candles[i].high;
          supplyLow = Math.min(candles[i].open, candles[i].close);
          supplyIdx = i;
        }
      }

      if (supplyIdx < 0 || !isFinite(supplyHigh)) return null;

      // 2. Identify CHoCH Low after Supply Drop
      let chochLevel = Infinity;
      let chochIdx = -1;
      for (let i = supplyIdx + 1; i < candles.length - 4; i++) {
        if (candles[i].low < chochLevel) {
          chochLevel = candles[i].low;
          chochIdx = i;
        }
      }

      if (chochIdx < 0 || !isFinite(chochLevel)) return null;

      // 3. Identify Inducement High ("X") between CHoCH and current bar
      let inducementHigh = -Infinity;
      let inducementIdx = -1;
      for (let i = chochIdx + 1; i < candles.length - 1; i++) {
        if (candles[i].high > inducementHigh) {
          inducementHigh = candles[i].high;
          inducementIdx = i;
        }
      }

      if (inducementIdx < 0 || !isFinite(inducementHigh)) {
        inducementHigh = chochLevel + (supplyHigh - chochLevel) * 0.50;
        inducementIdx = Math.round((chochIdx + candles.length - 1) / 2);
      }

      // 4. Equal Lows (EQL) Detection
      let eqlLevel = chochLevel;
      let hasEQL = false;
      for (let i = supplyIdx + 1; i < candles.length - 1; i++) {
        if (i !== chochIdx && Math.abs(candles[i].low - chochLevel) <= 0.60) {
          hasEQL = true;
          eqlLevel = Math.min(candles[i].low, chochLevel);
          break;
        }
      }

      // 5. Verify Inducement Purge and Supply Zone Tap
      const hasSweptInducement = currentBar.high >= (inducementHigh - 0.20);
      const hasTappedSupply = currentBar.high >= (supplyLow - 0.50) && currentBar.close <= (supplyHigh + 0.30);

      const range = currentBar.high - currentBar.low;
      const upperWick = currentBar.high - Math.max(currentBar.open, currentBar.close);
      const isRejection = (upperWick / (range + 0.001)) >= 0.28;
      const isBearishClose = currentBar.close < currentBar.open || (currentBar.close < (currentBar.high - range * 0.4));

      const entry = Number(currentBar.close).toFixed(2);
      const sl = (supplyHigh + 1.20).toFixed(2);
      const risk = Math.max(0.20, parseFloat(sl) - parseFloat(entry));
      
      let tp = (eqlLevel - 0.80).toFixed(2);
      if (parseFloat(entry) - parseFloat(tp) < risk * 3.5) {
        tp = (parseFloat(entry) - (risk * 4.5)).toFixed(2);
      }
      const reward = Math.max(0.10, parseFloat(entry) - parseFloat(tp));
      const rr = (reward / risk).toFixed(1);

      if (hasSweptInducement && hasTappedSupply && isRejection && isBearishClose) {
        return {
          indicatorName: "SMC Inducement & CHoCH Supply Sniper",
          direction: "SELL",
          isTriggered: true,
          stateBadge: "SUPPLY MITIGATION CONFIRMED",
          entry: entry,
          sl: sl,
          tp: tp,
          tp1: eqlLevel.toFixed(2),
          tp2: tp,
          rr: `1 : ${rr}`,
          risk: risk.toFixed(2),
          reward: reward.toFixed(2),
          supplyBox: { high: supplyHigh.toFixed(2), low: supplyLow.toFixed(2) },
          chochLevel: chochLevel.toFixed(2),
          eqlLevel: eqlLevel.toFixed(2),
          hasEQL: hasEQL,
          inducementLevel: inducementHigh.toFixed(2),
          inducementIdx: inducementIdx,
          reason: `Bearish CHoCH confirmed. Intermediate buyers trapped at Inducement (X) $${inducementHigh.toFixed(2)}. Extreme Supply Zone ($${supplyLow.toFixed(2)}-$${supplyHigh.toFixed(2)}) mitigated with rejection. Targeting EQL liquidity pool.`
        };
      }

      return {
        indicatorName: "SMC Inducement & CHoCH Supply Sniper",
        direction: "STANDBY",
        isTriggered: false,
        stateBadge: "WAITING FOR INDUCEMENT SWEEP",
        entry: (supplyLow).toFixed(2),
        sl: sl,
        tp: tp,
        tp1: eqlLevel.toFixed(2),
        rr: `1 : ${rr}`,
        risk: risk.toFixed(2),
        reward: reward.toFixed(2),
        supplyBox: { high: supplyHigh.toFixed(2), low: supplyLow.toFixed(2) },
        chochLevel: chochLevel.toFixed(2),
        eqlLevel: eqlLevel.toFixed(2),
        hasEQL: hasEQL,
        inducementLevel: inducementHigh.toFixed(2),
        inducementIdx: inducementIdx,
        reason: `Bearish CHoCH detected at $${chochLevel.toFixed(2)}. Extreme Supply at $${supplyLow.toFixed(2)}-$${supplyHigh.toFixed(2)}. Waiting for Inducement sweep at $${inducementHigh.toFixed(2)} and Supply mitigation.`
      };
    }
    window.evaluateSMC_InducementSupply = evaluateSMC_InducementSupply;

    // Dedicated Canvas Overlay for SMC Inducement & CHoCH Supply Sniper
    function drawSMC_InducementSupplyOverlay(ctx, setup, candles) {
      if (!ctx || !candleSeries || !chart) return;
      if (typeof indicatorSettings !== 'undefined' && !indicatorSettings.smcInducementSupply) return;
      if (!setup) return;

      ctx.save();

      // 1. Purple/Pink Semi-Transparent Box for Upper Supply Zone
      if (setup.supplyBox && setup.supplyBox.high && setup.supplyBox.low) {
        const yHigh = candleSeries.priceToCoordinate(Number(setup.supplyBox.high));
        const yLow = candleSeries.priceToCoordinate(Number(setup.supplyBox.low));
        if (yHigh !== null && yLow !== null) {
          const boxY = Math.min(yHigh, yLow);
          const boxH = Math.max(5, Math.abs(yLow - yHigh));
          const boxX = Math.max(10, canvasCssWidth - 280);
          const boxW = 210;

          ctx.fillStyle = 'rgba(217, 70, 239, 0.22)'; // Purple/Pink Supply Box
          ctx.fillRect(boxX, boxY, boxW, boxH);
          ctx.strokeStyle = 'rgba(217, 70, 239, 0.88)';
          ctx.lineWidth = 1.3;
          ctx.strokeRect(boxX, boxY, boxW, boxH);

          ctx.font = '700 9px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace';
          ctx.fillStyle = '#f0abfc';
          ctx.textBaseline = 'top';
          ctx.fillText(`SUPPLY · $${setup.supplyBox.low} - $${setup.supplyBox.high}`, boxX + 6, boxY + 3);
        }
      }

      // 2. Dotted Line at CHoCH Level
      if (setup.chochLevel) {
        const yCHoCH = candleSeries.priceToCoordinate(Number(setup.chochLevel));
        if (yCHoCH !== null && yCHoCH >= 10 && yCHoCH <= canvasCssHeight - 15) {
          ctx.strokeStyle = 'rgba(244, 63, 94, 0.85)';
          ctx.lineWidth = 1.2;
          ctx.setLineDash([4, 4]);
          ctx.beginPath();
          ctx.moveTo(30, yCHoCH);
          ctx.lineTo(canvasCssWidth - 65, yCHoCH);
          ctx.stroke();
          ctx.setLineDash([]);

          const chText = `CHOCH · $${Number(setup.chochLevel).toFixed(2)}`;
          ctx.font = '700 9px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace';
          const tw = ctx.measureText(chText).width;
          const bw = Math.round(tw + 8);
          const bh = 15;
          const bx = 35;
          const by = Math.round(yCHoCH - bh / 2);

          ctx.fillStyle = 'rgba(15, 23, 42, 0.92)';
          ctx.fillRect(bx, by, bw, bh);
          ctx.strokeStyle = 'rgba(244, 63, 94, 0.85)';
          ctx.strokeRect(bx, by, bw, bh);
          ctx.fillStyle = '#fb7185';
          ctx.textBaseline = 'middle';
          ctx.fillText(chText, bx + 4, yCHoCH);
        }
      }

      // 3. Blue Trendline / Level Line Marking Internal Liquidity ("LIQUIDITY" + "X")
      if (setup.inducementLevel) {
        const yInd = candleSeries.priceToCoordinate(Number(setup.inducementLevel));
        if (yInd !== null && yInd >= 10 && yInd <= canvasCssHeight - 15) {
          ctx.strokeStyle = 'rgba(56, 189, 248, 0.85)';
          ctx.lineWidth = 1.3;
          ctx.setLineDash([3, 3]);
          ctx.beginPath();
          ctx.moveTo(30, yInd);
          ctx.lineTo(canvasCssWidth - 65, yInd);
          ctx.stroke();
          ctx.setLineDash([]);

          const indText = `LIQUIDITY (X) · $${Number(setup.inducementLevel).toFixed(2)}`;
          ctx.font = '700 9.5px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace';
          const tw = ctx.measureText(indText).width;
          const bw = Math.round(tw + 10);
          const bh = 16;
          const bx = canvasCssWidth - bw - 70;
          const by = Math.round(yInd - bh / 2);

          ctx.fillStyle = 'rgba(15, 23, 42, 0.92)';
          ctx.fillRect(bx, by, bw, bh);
          ctx.strokeStyle = 'rgba(56, 189, 248, 0.85)';
          ctx.lineWidth = 1;
          ctx.strokeRect(bx, by, bw, bh);
          ctx.fillStyle = '#38bdf8';
          ctx.textBaseline = 'middle';
          ctx.fillText(indText, bx + 5, yInd);
        }
      }

      // 4. Dotted Line Marking Lower "EQL" Target
      if (setup.eqlLevel) {
        const yEQL = candleSeries.priceToCoordinate(Number(setup.eqlLevel));
        if (yEQL !== null && yEQL >= 10 && yEQL <= canvasCssHeight - 15) {
          ctx.strokeStyle = 'rgba(251, 191, 36, 0.85)';
          ctx.lineWidth = 1.2;
          ctx.setLineDash([3, 3]);
          ctx.beginPath();
          ctx.moveTo(30, yEQL);
          ctx.lineTo(canvasCssWidth - 65, yEQL);
          ctx.stroke();
          ctx.setLineDash([]);

          const eqlText = `EQL · $${Number(setup.eqlLevel).toFixed(2)}`;
          ctx.font = '700 9px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace';
          const tw = ctx.measureText(eqlText).width;
          const bw = Math.round(tw + 8);
          const bh = 15;
          const bx = 35;
          const by = Math.round(yEQL - bh / 2);

          ctx.fillStyle = 'rgba(15, 23, 42, 0.92)';
          ctx.fillRect(bx, by, bw, bh);
          ctx.strokeStyle = 'rgba(251, 191, 36, 0.85)';
          ctx.strokeRect(bx, by, bw, bh);
          ctx.fillStyle = '#fbbf24';
          ctx.textBaseline = 'middle';
          ctx.fillText(eqlText, bx + 4, yEQL);
        }
      }

      // 5. Text Watermark during Waiting Phase
      if (!setup.isTriggered) {
        ctx.font = '800 20px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace';
        ctx.fillStyle = 'rgba(217, 70, 239, 0.28)'; // Semi-transparent pink/purple
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        const wmX = Math.round(canvasCssWidth * 0.55);
        const wmY = Math.round(canvasCssHeight * 0.40);
        ctx.fillText('WAITING FOR INDUCEMENT SWEEP', wmX, wmY);
        ctx.font = '700 10.5px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace';
        ctx.fillStyle = 'rgba(217, 70, 239, 0.22)';
        ctx.fillText('SMC CHoCH + Extreme Supply Monitor Active', wmX, wmY + 18);
      }

      // 6. TradingView Style Short Position Tool on Trigger
      if (setup.isTriggered && setup.entry && setup.sl && setup.tp) {
        const yEntry = candleSeries.priceToCoordinate(Number(setup.entry));
        const ySL = candleSeries.priceToCoordinate(Number(setup.sl));
        const yTP = candleSeries.priceToCoordinate(Number(setup.tp));

        if (yEntry !== null && ySL !== null && yTP !== null) {
          let lastCandleX = null;
          if (candles && candles.length) {
            lastCandleX = chart.timeScale().timeToCoordinate(candles[candles.length - 1].time);
          }
          const startX = (lastCandleX !== null && lastCandleX > 40 && lastCandleX < canvasCssWidth - 165)
            ? Math.round(lastCandleX + 16)
            : Math.round(canvasCssWidth - 190);
          const boxW = Math.max(110, Math.min(145, canvasCssWidth - startX - 68));
          const endX = startX + boxW;

          // Red Risk Box (SL) - Above Supply Ceiling
          const riskTopY = Math.min(ySL, yEntry);
          const riskBotY = Math.max(ySL, yEntry);
          const riskH = Math.max(4, riskBotY - riskTopY);

          ctx.fillStyle = 'rgba(248, 81, 73, 0.25)';
          ctx.fillRect(startX, riskTopY, boxW, riskH);
          ctx.strokeStyle = 'rgba(248, 81, 73, 0.90)';
          ctx.lineWidth = 1.2;
          ctx.strokeRect(startX, riskTopY, boxW, riskH);

          // Green Reward Box (TP) - Extending down through EQL Target
          const rewTopY = Math.min(yEntry, yTP);
          const rewBotY = Math.max(yEntry, yTP);
          const rewH = Math.max(4, rewBotY - rewTopY);

          ctx.fillStyle = 'rgba(46, 160, 67, 0.22)';
          ctx.fillRect(startX, rewTopY, boxW, rewH);
          ctx.strokeStyle = 'rgba(46, 160, 67, 0.90)';
          ctx.lineWidth = 1.2;
          ctx.strokeRect(startX, rewTopY, boxW, rewH);

          // Entry Midline
          ctx.strokeStyle = '#ffffff';
          ctx.lineWidth = 1.6;
          ctx.beginPath();
          ctx.moveTo(startX, yEntry);
          ctx.lineTo(endX, yEntry);
          ctx.stroke();

          // Pills
          ctx.font = '700 9.5px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace';
          ctx.textAlign = 'left';
          ctx.textBaseline = 'middle';

          // SL pill
          const slTxt = `SL $${Number(setup.sl).toFixed(1)} (-$${Number(setup.risk).toFixed(1)})`;
          const slW = ctx.measureText(slTxt).width + 8;
          ctx.fillStyle = 'rgba(15, 23, 42, 0.92)';
          ctx.fillRect(startX + 4, riskTopY + 2, slW, 14);
          ctx.fillStyle = '#ff5252';
          ctx.fillText(slTxt, startX + 8, riskTopY + 9);

          // TP pill (EQL Liquidity Target)
          const tpTxt = `EQL TP $${Number(setup.tp).toFixed(1)} (+$${Number(setup.reward).toFixed(1)}) · ${setup.rr} RR`;
          const tpW = ctx.measureText(tpTxt).width + 8;
          ctx.fillStyle = 'rgba(15, 23, 42, 0.92)';
          ctx.fillRect(startX + 4, rewBotY - 16, tpW, 14);
          ctx.fillStyle = '#3fb950';
          ctx.fillText(tpTxt, startX + 8, rewBotY - 9);

          // Entry pill
          const entTxt = `Supply Tap Entry $${Number(setup.entry).toFixed(1)}`;
          const entW = ctx.measureText(entTxt).width + 8;
          ctx.fillStyle = 'rgba(15, 23, 42, 0.92)';
          ctx.fillRect(startX + 4, yEntry - 7, entW, 14);
          ctx.fillStyle = '#ffffff';
          ctx.fillText(entTxt, startX + 8, yEntry);
        }
      }

      ctx.restore();
    }
    window.drawSMC_InducementSupplyOverlay = drawSMC_InducementSupplyOverlay;

    '''
    if engine_needle not in html:
        print("ERROR: engine_needle not found!")
        return False
    html = html.replace(engine_needle, engine_code + engine_needle, 1)

    # 7. modularEngineState initial state:
    # Add CHOCH_SUPPLY into modularEngineState
    modstate_needle = "indicators: {\n        OB_FIBO: {"
    alt_modstate = "indicators: {\r\n        OB_FIBO: {"
    modstate_replace = '''indicators: {
        CHOCH_SUPPLY: { status: 'STANDBY', stateBadge: 'WAITING FOR INDUCEMENT SWEEP', direction: 'NEUTRAL', entry: '--', sl: '--', tp: '--', rr: '--', reason: 'Scanning 5M/15M Structure for CHoCH & Supply Zone' },
        OB_FIBO: {'''
    if modstate_needle in html:
        html = html.replace(modstate_needle, modstate_replace, 1)
    elif alt_modstate in html:
        html = html.replace(alt_modstate, modstate_replace, 1)
    else:
        print("ERROR: modstate_needle not found!")
        return False

    # 8. In updateModularEngineTelemetry:
    # Evaluate SMC Inducement & CHoCH Supply Sniper and populate modularEngineState.indicators.CHOCH_SUPPLY
    telemetry_needle = '// 1. SMC TELEMETRY'
    telemetry_code = '''// Dedicated: SMC INDUCEMENT & CHOCH SUPPLY SNIPER TELEMETRY
      const inducementResult = evaluateSMC_InducementSupply(m5Candles);
      window.latestSMC_InducementSupply = inducementResult;

      if (inducementResult) {
        if (inducementResult.isTriggered) {
          modularEngineState.indicators.CHOCH_SUPPLY = {
            status: 'SUPPLY MITIGATION CONFIRMED',
            stateBadge: 'SUPPLY MITIGATION CONFIRMED',
            direction: 'SELL / SHORT',
            entry: '$' + Number(inducementResult.entry).toFixed(2),
            sl: '$' + Number(inducementResult.sl).toFixed(2),
            tp: '$' + Number(inducementResult.tp).toFixed(2),
            rr: inducementResult.rr || '1 : 5.0',
            reason: inducementResult.reason || 'Bearish CHoCH confirmed. Intermediate buyers trapped at Inducement (X). Extreme Supply Zone mitigated with rejection. Targeting EQL liquidity pool.'
          };
        } else {
          modularEngineState.indicators.CHOCH_SUPPLY = {
            status: 'WAITING FOR INDUCEMENT SWEEP',
            stateBadge: 'WAITING FOR INDUCEMENT SWEEP',
            direction: 'STANDBY',
            entry: '$' + Number(inducementResult.entry || inducementResult.supplyBox.low).toFixed(2),
            sl: '$' + Number(inducementResult.sl).toFixed(2),
            tp: '$' + Number(inducementResult.tp).toFixed(2),
            rr: inducementResult.rr || '1 : 5.0',
            reason: inducementResult.reason || 'Bearish CHoCH detected. Waiting for Inducement sweep and Extreme Supply mitigation.'
          };
        }
      } else {
        modularEngineState.indicators.CHOCH_SUPPLY = {
          status: 'STANDBY',
          stateBadge: 'STANDBY',
          direction: 'NEUTRAL',
          entry: '--',
          sl: '--',
          tp: '--',
          rr: '--',
          reason: 'Awaiting 5M/15M CHoCH & Extreme Supply formation.'
        };
      }

      // 1. SMC TELEMETRY'''
    if telemetry_needle not in html:
        print("ERROR: telemetry_needle not found!")
        return False
    html = html.replace(telemetry_needle, telemetry_code, 1)

    # 9. In renderModularTelemetryUI:
    # Update tabs list to include 'CHOCH_SUPPLY'
    tabs_needle = "const tabs = ['SMC', 'OB_FIBO', 'LIQUIDITY', 'DLS', 'VWAP_FVG', 'FIBONACCI', 'BREAKOUT'];"
    tabs_replace = "const tabs = ['SMC', 'OB_FIBO', 'CHOCH_SUPPLY', 'LIQUIDITY', 'DLS', 'VWAP_FVG', 'FIBONACCI', 'BREAKOUT'];"
    if tabs_needle not in html:
        print("ERROR: tabs_needle not found!")
        return False
    html = html.replace(tabs_needle, tabs_replace, 1)

    # Header label in modular card:
    header_needle = "${activeTab === 'OB_FIBO' ? '⚡ SMC PULLBACK SNIPER (OB + 0.618 FIB)' : (activeTab === 'VWAP_FVG' ? 'VWAP + FVG' : activeTab)} Indicator Engine"
    header_replace = "${activeTab === 'OB_FIBO' ? '⚡ SMC PULLBACK SNIPER (OB + 0.618 FIB)' : (activeTab === 'CHOCH_SUPPLY' ? '⚡ SMC INDUCEMENT & CHOCH SUPPLY SNIPER' : (activeTab === 'VWAP_FVG' ? 'VWAP + FVG' : activeTab))} Indicator Engine"
    if header_needle not in html:
        print("ERROR: header_needle not found!")
        return False
    html = html.replace(header_needle, header_replace, 1)

    # Tab button text:
    tabbtn_needle = "${tab === 'VWAP_FVG' ? 'VWAP+FVG' : (tab === 'OB_FIBO' ? 'OB+FIB 🎯' : tab)}"
    tabbtn_replace = "${tab === 'VWAP_FVG' ? 'VWAP+FVG' : (tab === 'OB_FIBO' ? 'OB+FIB 🎯' : (tab === 'CHOCH_SUPPLY' ? 'CHOCH ⚡' : tab))}"
    if tabbtn_needle not in html:
        print("ERROR: tabbtn_needle not found!")
        return False
    html = html.replace(tabbtn_needle, tabbtn_replace, 1)

    # State badge in header:
    badge_needle = "${activeTab === 'OB_FIBO' && activeData.stateBadge ? activeData.stateBadge : activeData.direction}"
    badge_replace = "${(activeTab === 'OB_FIBO' || activeTab === 'CHOCH_SUPPLY') && activeData.stateBadge ? activeData.stateBadge : activeData.direction}"
    if badge_needle not in html:
        print("ERROR: badge_needle not found!")
        return False
    html = html.replace(badge_needle, badge_replace, 1)

    # 10. In redrawDrawings():
    # Hook drawSMC_InducementSupplyOverlay
    redraw_needle = '// Dedicated: SMC M5 Pullback Sniper Overlay (BOS + OB + 0.618 Fibo + IFVG TP)'
    redraw_code = '''// Dedicated: SMC Inducement & CHoCH Supply Sniper Overlay
      if (typeof indicatorSettings !== 'undefined' && indicatorSettings.smcInducementSupply) {
        drawSMC_InducementSupplyOverlay(drawingCtx, window.latestSMC_InducementSupply, (typeof rawCandleData !== 'undefined' ? rawCandleData : []));
      }

      // Dedicated: SMC M5 Pullback Sniper Overlay (BOS + OB + 0.618 Fibo + IFVG TP)'''
    if redraw_needle not in html:
        print("ERROR: redraw_needle not found!")
        return False
    html = html.replace(redraw_needle, redraw_code, 1)

    # Also hook into showRROverlay if triggered:
    rr_needle = '} else if (typeof indicatorSettings !== \'undefined\' && indicatorSettings.smcPullbackSniper && window.latestSMC_OB_Fibo && window.latestSMC_OB_Fibo.isTriggered) {'
    rr_code = '''} else if (typeof indicatorSettings !== 'undefined' && indicatorSettings.smcInducementSupply && window.latestSMC_InducementSupply && window.latestSMC_InducementSupply.isTriggered) {
          const sniper = window.latestSMC_InducementSupply;
          drawRiskRewardOverlay(drawingCtx, {
            type: 'SHORT',
            entry: Number(sniper.entry),
            sl: Number(sniper.sl),
            tp: Number(sniper.tp),
            risk: Number(sniper.risk),
            reward: Number(sniper.reward),
            rrRatio: sniper.rr ? sniper.rr.replace('1 : ', '') : '5.0'
          });
        } else if (typeof indicatorSettings !== 'undefined' && indicatorSettings.smcPullbackSniper && window.latestSMC_OB_Fibo && window.latestSMC_OB_Fibo.isTriggered) {'''
    if rr_needle not in html:
        print("ERROR: rr_needle not found!")
        return False
    html = html.replace(rr_needle, rr_code, 1)

    # Save to gold_dashboard.html, index.html, deep_analysis_gold.html
    for fname in ['gold_dashboard.html', 'index.html', 'deep_analysis_gold.html']:
        with open(fname, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"Successfully updated {fname} ({len(html)} bytes)")

    return True

if __name__ == '__main__':
    ok = main()
    if not ok:
        sys.exit(1)
